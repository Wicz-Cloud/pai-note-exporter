"""Plaud.ai export functionality using REST API."""

from pathlib import Path
from typing import Any

import httpx

from pai_note_exporter.config import Config
from pai_note_exporter.exceptions import APIError
from pai_note_exporter.logger import setup_logger


class PlaudAIExporter:
    """Handle file export from Plaud.ai using REST API.

    This class provides methods to list recordings and export transcriptions/audio
    using the Plaud.ai REST API endpoints discovered from HAR analysis.

    Attributes:
        config: Configuration object with credentials and settings
        logger: Logger instance for this class
        client: HTTP client for API calls
        token: Authentication token for API requests
        base_url: Base URL for Plaud.ai API
    """

    BASE_URL = "https://api.plaud.ai"

    def __init__(self, config: Config, token: str) -> None:
        """Initialize the PlaudAIExporter instance.

        Args:
            config: Configuration object with credentials and settings
            token: Authentication token from login
        """
        self.config = config
        self.token = token
        self.logger = setup_logger(
            name=__name__,
            log_level=config.log_level,
            log_file=config.log_file,
        )

        # Generate device ID (same format as seen in HAR file)
        import uuid
        device_id = str(uuid.uuid4()).replace('-', '')[:18]  # 18 chars like in HAR

        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {token}",
                "edit-from": "web",
                "app-platform": "web",
                "x-device-id": device_id,
                "x-pld-tag": device_id,
                "Content-Type": "application/json",
            }
        )

    async def __aenter__(self) -> "PlaudAIExporter":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Async context manager exit."""
        await self.client.aclose()

    async def list_files(
        self,
        skip: int = 0,
        limit: int = 20,
        is_trash: int = 2,
        sort_by: str = "start_time",
        is_desc: bool = True
    ) -> list[dict[str, Any]]:
        """List files from Plaud.ai.

        Args:
            skip: Number of files to skip (pagination)
            limit: Maximum number of files to return
            is_trash: Trash filter (2 = not in trash)
            sort_by: Sort field
            is_desc: Sort descending

        Returns:
            List of file dictionaries

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.BASE_URL}/file/simple/web"
        params = {
            "skip": skip,
            "limit": limit,
            "is_trash": is_trash,
            "sort_by": sort_by,
            "is_desc": is_desc,
        }

        try:
            self.logger.debug(f"Listing files: {params}")
            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            self.logger.debug(f"Raw API response: {data}")
            # The API returns an object with data_file_list containing the files
            files = data.get("data_file_list", [])

            # Filter out files in trash as additional safety measure
            # (API parameter is_trash=2 should do this, but filter client-side too)
            files = [f for f in files if not f.get("is_trash", False)]

            self.logger.info(f"Retrieved {len(files)} files (filtered out trash)")
            return files

        except httpx.HTTPStatusError as e:
            self.logger.error(f"API error listing files: {e.response.status_code} - {e.response.text}")
            raise APIError(f"Failed to list files: {e.response.status_code}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error listing files: {e}")
            raise APIError(f"Unexpected error listing files: {e}") from e

    async def get_transcription_content(self, file_id: str) -> str | None:
        """Get transcription content for a file using various API endpoints.

        Args:
            file_id: ID of the file

        Returns:
            Transcription content as string, or None if not available

        Raises:
            APIError: If the API request fails
        """
        # Try multiple endpoints that might contain transcription data

        # 1. Try /ai/transsumm/{file_id} - looks most promising
        try:
            url = f"{self.BASE_URL}/ai/transsumm/{file_id}"
            self.logger.debug(f"Trying /ai/transsumm/{file_id}")
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            self.logger.debug(f"/ai/transsumm response: {data}")

            # Check if it contains transcription data
            if data.get("status") == 0 and "data" in data:
                trans_data = data["data"]
                if isinstance(trans_data, dict) and "trans_result" in trans_data:
                    trans_result = trans_data["trans_result"]
                    if isinstance(trans_result, list) and trans_result:
                        # Convert transcription segments to text
                        content = ""
                        for segment in trans_result:
                            if isinstance(segment, dict) and "content" in segment:
                                content += segment["content"] + " "
                        return content.strip()
            elif data.get("status") == -1:
                self.logger.debug(f"/ai/transsumm failed: {data.get('msg')}")

        except Exception as e:
            self.logger.debug(f"/ai/transsumm failed: {e}")

        # 2. Try /file/{file_id} - detailed file endpoint
        try:
            url = f"{self.BASE_URL}/file/{file_id}"
            self.logger.debug(f"Trying /file/{file_id}")
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            self.logger.debug(f"/file/{file_id} response: {data}")

            if data.get("status") == 0 and "data" in data:
                file_data = data["data"]
                if isinstance(file_data, dict) and "trans_result" in file_data:
                    trans_result = file_data["trans_result"]
                    if isinstance(trans_result, list) and trans_result:
                        # Convert transcription segments to text
                        content = ""
                        for segment in trans_result:
                            if isinstance(segment, dict) and "content" in segment:
                                content += segment["content"] + " "
                        return content.strip()

        except Exception as e:
            self.logger.debug(f"/file/{file_id} failed: {e}")

        # 3. Try /ai/query_note with file-id header - this is the working endpoint
        try:
            url = f"{self.BASE_URL}/ai/query_note"
            self.logger.debug("Trying /ai/query_note with file-id header")
            response = await self.client.get(url, headers={"file-id": file_id})
            response.raise_for_status()
            data = response.json()
            self.logger.debug(f"/ai/query_note response: {data}")

            if data.get("status") == 0 and "data" in data:
                query_data = data["data"]
                if isinstance(query_data, list) and query_data:
                    # Get the first item (should contain transcription data)
                    item = query_data[0]
                    if isinstance(item, dict) and "data_content" in item:
                        content = item["data_content"]
                        if isinstance(content, str) and content.strip():
                            self.logger.info(f"Found transcription content via /ai/query_note: {len(content)} chars")
                            return content.strip()

        except Exception as e:
            self.logger.debug(f"/ai/query_note failed: {e}")

        except Exception as e:
            self.logger.debug(f"/ai/query_note failed: {e}")

        self.logger.debug(f"No transcription content found for file {file_id}")
        return None

    async def get_temp_url(self, file_id: str) -> str:
        """Get temporary download URL for a file.

        Args:
            file_id: ID of the file

        Returns:
            Temporary download URL

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.BASE_URL}/file/temp-url/{file_id}"

        # Generate request ID (similar format to what was seen in HAR)
        import uuid
        request_id = str(uuid.uuid4()).replace('-', '')[:11]  # 11 chars like in HAR

        headers = {"x-request-id": request_id}

        try:
            self.logger.debug(f"Getting temp URL for file {file_id}")
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            self.logger.debug(f"Temp URL response: {data}")

            if data.get("status") == 0 and "temp_url" in data:
                temp_url = data["temp_url"]
                if isinstance(temp_url, str) and temp_url.startswith("https://"):
                    self.logger.info(f"Got temp URL for file {file_id}")
                    return temp_url
                else:
                    self.logger.error(f"Invalid temp URL format: {temp_url}")
                    raise APIError(f"Invalid temp URL format: {temp_url}")
            else:
                error_msg = data.get('msg', 'Unknown error')
                self.logger.error(f"Temp URL API returned error: {error_msg}")
                raise APIError(f"Failed to get temp URL: {error_msg}")

        except httpx.HTTPStatusError as e:
            self.logger.error(f"API error getting temp URL: {e.response.status_code} - {e.response.text}")
            raise APIError(f"Failed to get temp URL: {e.response.status_code}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting temp URL: {e}")
            raise APIError(f"Unexpected error getting temp URL: {e}") from e

    async def export_transcription(
        self,
        file_id: str,
        prompt_type: str = "trans",
        to_format: str = "TXT",
        title: str | None = None,
        create_time: str | None = None,
        with_speaker: int = 0,
        with_timestamp: int = 0,
        content: str | None = None
    ) -> bytes:
        """Export transcription/summary for a file.

        Args:
            file_id: ID of the file
            prompt_type: Type of content ("trans" for transcription, "summary" for summary)
            to_format: Export format ("TXT", "DOCX", "PDF", "SRT")
            title: Title for the export
            create_time: Creation time string
            with_speaker: Include speaker labels (0 or 1)
            with_timestamp: Include timestamps (0 or 1)
            content: Content to export

        Returns:
            Exported file content as bytes

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.BASE_URL}/file/document/export"

        payload = {
            "file_id": file_id,
            "prompt_type": prompt_type,
            "to_format": to_format.upper(),
            "title": title,
            "create_time": create_time or "",
            "with_speaker": with_speaker,
            "with_timestamp": with_timestamp,
        }

        if prompt_type == "trans":
            # For transcription, don't pass content - let the API generate it server-side
            pass
        elif prompt_type == "summary":
            if content:
                payload["summary_content"] = content

        try:
            self.logger.debug(f"Exporting {prompt_type} for file {file_id} as {to_format}")
            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            # The response should contain the file data
            if response.headers.get("content-type") == "application/json":
                data = response.json()
                self.logger.debug(f"Export API response: {data}")
                if data.get("status") == 0 and "data" in data:
                    # Return the data field which should contain the file content
                    return data["data"]
                elif data.get("status") == -1:
                    error_msg = data.get('msg', 'Unknown error')
                    self.logger.error(f"Export API returned error: {error_msg}")
                    raise APIError(f"Export failed: {error_msg}")
                else:
                    # Maybe the content is in the response directly
                    self.logger.debug(f"Response content type: {response.headers.get('content-type')}")
                    self.logger.debug(f"Response headers: {dict(response.headers)}")
                    # Check if response has content
                    if hasattr(response, 'content') and response.content:
                        return response.content
                    else:
                        self.logger.error(f"Unexpected response format: {data}")
                        raise APIError(f"Unexpected response format: {data}")
            else:
                # Direct file content
                return response.content

        except httpx.HTTPStatusError as e:
            self.logger.error(f"API error exporting transcription: {e.response.status_code} - {e.response.text}")
            raise APIError(f"Failed to export transcription: {e.response.status_code}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error exporting transcription: {e}")
            raise APIError(f"Unexpected error exporting transcription: {e}") from e

    async def download_file(self, url: str, filename: str, output_dir: Path) -> Path:
        """Download a file from a URL.

        Args:
            url: URL to download from
            filename: Filename to save as
            output_dir: Directory to save the file in

        Returns:
            Path to the downloaded file

        Raises:
            APIError: If the download fails
        """
        output_path = output_dir / filename
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.logger.info(f"Downloading {filename} to {output_path}")
            async with httpx.AsyncClient(timeout=60.0) as download_client:
                async with download_client.stream("GET", url) as response:
                    response.raise_for_status()

                    with open(output_path, "wb") as f:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)

            self.logger.info(f"Successfully downloaded {filename}")
            return output_path

        except Exception as e:
            self.logger.error(f"Error downloading file: {e}")
            raise APIError(f"Failed to download file: {e}") from e

    def format_file_info(self, file_info: dict[str, Any]) -> str:
        """Format file information for display.

        Args:
            file_info: File information dictionary

        Returns:
            Formatted string with file details
        """
        file_id = file_info.get("id", "Unknown")
        filename = file_info.get("filename", "Unknown")
        duration = file_info.get("duration", 0)
        start_time = file_info.get("start_time", 0)

        # Format duration
        minutes = duration // 60
        seconds = duration % 60
        duration_str = f"{minutes}:{seconds:02d}"

        # Format start time (assuming Unix timestamp)
        from datetime import datetime
        try:
            dt = datetime.fromtimestamp(start_time)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = str(start_time)

        return f"[{file_id[:8]}] {filename} - {duration_str} - {time_str}"

    async def probe_ai_query_source(self, file_id: str) -> dict[str, Any]:
        """Probe the /ai/query_source endpoint with a specific file ID.

        Args:
            file_id: The file ID to query for

        Returns:
            API response data

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.BASE_URL}/ai/query_source"

        try:
            self.logger.debug(f"Probing /ai/query_source for file {file_id}")
            response = await self.client.get(url, headers={"file-id": file_id})
            response.raise_for_status()

            data = response.json()
            self.logger.debug(f"/ai/query_source response: {data}")
            return data

        except httpx.HTTPStatusError as e:
            self.logger.error(f"API error probing /ai/query_source: {e.response.status_code} - {e.response.text}")
            raise APIError(f"Failed to probe /ai/query_source: {e.response.status_code}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error probing /ai/query_source: {e}")
            raise APIError(f"Unexpected error probing /ai/query_source: {e}") from e

    async def probe_ai_trans_status(self) -> dict[str, Any]:
        """Probe the /ai/trans-status endpoint.

        Returns:
            API response data

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.BASE_URL}/ai/trans-status"

        try:
            self.logger.debug("Probing /ai/trans-status")
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            self.logger.debug(f"/ai/trans-status response: {data}")
            return data

        except httpx.HTTPStatusError as e:
            self.logger.error(f"API error probing /ai/trans-status: {e.response.status_code} - {e.response.text}")
            raise APIError(f"Failed to probe /ai/trans-status: {e.response.status_code}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error probing /ai/trans-status: {e}")
            raise APIError(f"Unexpected error probing /ai/trans-status: {e}") from e

    async def probe_file_list_detailed(self) -> list[dict[str, Any]]:
        """Probe the /file/list endpoint with support_mul_summ=true as query parameter.

        Returns:
            List of files from detailed endpoint

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.BASE_URL}/file/list?support_mul_summ=true"

        try:
            self.logger.debug("Probing /file/list with support_mul_summ=true")
            response = await self.client.post(url)
            response.raise_for_status()

            data = response.json()
            self.logger.debug(f"/file/list detailed response: {data}")

            files = data.get("data_file_list", [])
            self.logger.info(f"Retrieved {len(files)} files from detailed endpoint")
            return files

        except httpx.HTTPStatusError as e:
            self.logger.error(f"API error probing /file/list detailed: {e.response.status_code} - {e.response.text}")
            raise APIError(f"Failed to probe /file/list detailed: {e.response.status_code}") from e
    async def probe_ai_query_note(self, file_id: str) -> dict[str, Any]:
        """Probe the /ai/query_note endpoint with a specific file ID.

        Args:
            file_id: The file ID to query for

        Returns:
            API response data

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.BASE_URL}/ai/query_note"

        try:
            self.logger.debug(f"Probing /ai/query_note for file {file_id}")
            response = await self.client.get(url, headers={"file-id": file_id})
            response.raise_for_status()

            data = response.json()
            self.logger.debug(f"/ai/query_note response: {data}")
            return data

        except httpx.HTTPStatusError as e:
            self.logger.error(f"API error probing /ai/query_note: {e.response.status_code} - {e.response.text}")
            raise APIError(f"Failed to probe /ai/query_note: {e.response.status_code}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error probing /ai/query_note: {e}")
            raise APIError(f"Unexpected error probing /ai/query_note: {e}") from e
