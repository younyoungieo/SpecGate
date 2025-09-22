"""
Confluence 서비스
Confluence 통합 기능을 제공하는 메인 서비스 클래스
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from .client import ConfluenceAPIClient
from .transformer import ConfluenceDataTransformer


class ConfluenceService:
    """Confluence 서비스"""
    
    def __init__(self):
        self.client = ConfluenceAPIClient()
        self.transformer = ConfluenceDataTransformer()
        self.logger = logging.getLogger("specgate.confluence.service")
    
    async def fetch_documents(
        self, 
        label: str, 
        space_key: Optional[str] = None, 
        limit: int = 10,
        save_html: bool = True,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """라벨 기준으로 문서 수집"""
        self.logger.info(f"Confluence 문서 수집 시작 - 라벨: {label}, 스페이스: {space_key}")
        
        try:
            # 1단계: CQL 쿼리 생성
            cql_query = self.client.generate_cql_query(label, space_key)
            self.logger.info(f"CQL 쿼리: {cql_query}")
            
            # 2단계: Confluence API 호출
            self.logger.info("Confluence API 호출 중...")
            confluence_response = await self.client.search_content(cql_query, limit)
            
            # 3단계: SpecGate 형식으로 변환
            self.logger.info("SpecGate 형식으로 변환 중...")
            specgate_documents = self.transformer.transform_batch_to_specgate_format(confluence_response)
            
            # 4단계: HTML 원본 저장 (새로 추가)
            html_files = []
            if save_html:
                html_files = await self._save_html_files(specgate_documents, label, output_dir)
            
            # 5단계: 메타데이터 생성
            metadata = self._create_metadata(label, space_key, cql_query, confluence_response)
            metadata["html_files"] = html_files  # HTML 파일 경로 추가
            
            result = {
                "status": "success",
                "documents": specgate_documents,
                "metadata": metadata
            }
            
            self.logger.info(f"총 {len(specgate_documents)}개 문서 수집 완료")
            if save_html:
                self.logger.info(f"HTML 원본 {len(html_files)}개 파일 저장 완료")
            return result
            
        except Exception as e:
            self.logger.error(f"Confluence 문서 수집 실패: {str(e)}")
            return self._create_error_result(str(e), label, space_key)
    
    async def fetch_document_by_id(self, content_id: str) -> Dict[str, Any]:
        """ID로 특정 문서 조회"""
        self.logger.info(f"Confluence 문서 조회 시작 - ID: {content_id}")
        
        try:
            # 1단계: Confluence API 호출
            confluence_response = await self.client.get_content_by_id(content_id)
            
            # 2단계: SpecGate 형식으로 변환
            specgate_document = self.transformer.transform_to_specgate_format(
                {"results": [confluence_response]}
            )
            
            result = {
                "status": "success",
                "document": specgate_document,
                "metadata": {
                    "content_id": content_id,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            self.logger.info(f"문서 조회 완료 - 제목: {specgate_document.get('title', 'Unknown')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Confluence 문서 조회 실패: {str(e)}")
            return self._create_error_result(str(e), content_id=content_id)
    
    async def search_by_cql(self, cql_query: str, limit: int = 10) -> Dict[str, Any]:
        """CQL 쿼리로 직접 검색"""
        self.logger.info(f"CQL 검색 시작 - 쿼리: {cql_query}")
        
        try:
            # 1단계: Confluence API 호출
            confluence_response = await self.client.search_content(cql_query, limit)
            
            # 2단계: SpecGate 형식으로 변환
            specgate_documents = self.transformer.transform_batch_to_specgate_format(confluence_response)
            
            # 3단계: 메타데이터 생성
            metadata = self._create_metadata_from_cql(cql_query, confluence_response)
            
            result = {
                "status": "success",
                "documents": specgate_documents,
                "metadata": metadata
            }
            
            self.logger.info(f"CQL 검색 완료 - {len(specgate_documents)}개 문서 발견")
            return result
            
        except Exception as e:
            self.logger.error(f"CQL 검색 실패: {str(e)}")
            return self._create_error_result(str(e), cql_query=cql_query)
    
    def _create_metadata(
        self, 
        label: str, 
        space_key: Optional[str], 
        cql_query: str, 
        confluence_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """메타데이터 생성"""
        transformer_metadata = self.transformer.extract_metadata(confluence_response)
        
        return {
            "total_count": transformer_metadata.get("total_count", 0),
            "search_label": label,
            "space_key": space_key,
            "cql_query": cql_query,
            "timestamp": datetime.now().isoformat(),
            "confluence_api_version": "direct_api_call",
            "has_more": transformer_metadata.get("has_more", False)
        }
    
    def _create_metadata_from_cql(self, cql_query: str, confluence_response: Dict[str, Any]) -> Dict[str, Any]:
        """CQL 검색용 메타데이터 생성"""
        transformer_metadata = self.transformer.extract_metadata(confluence_response)
        
        return {
            "total_count": transformer_metadata.get("total_count", 0),
            "cql_query": cql_query,
            "timestamp": datetime.now().isoformat(),
            "confluence_api_version": "direct_api_call",
            "has_more": transformer_metadata.get("has_more", False)
        }
    
    def _create_error_result(
        self, 
        error_message: str, 
        label: Optional[str] = None, 
        space_key: Optional[str] = None,
        content_id: Optional[str] = None,
        cql_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """에러 결과 생성"""
        metadata = {
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        if label is not None:
            metadata["search_label"] = label
        if space_key is not None:
            metadata["space_key"] = space_key
        if content_id is not None:
            metadata["content_id"] = content_id
        if cql_query is not None:
            metadata["cql_query"] = cql_query
        
        return {
            "status": "error",
            "documents": [],
            "metadata": metadata
        }
    
    def is_available(self) -> bool:
        """Confluence 서비스 사용 가능 여부 확인"""
        return self.client.is_configured()
    
    async def _save_html_files(self, documents: List[Dict[str, Any]], label: str, output_dir: Optional[str] = None) -> List[str]:
        """HTML 원본을 파일로 저장"""
        import os
        import aiofiles
        from datetime import datetime
        
        try:
            # 출력 디렉토리 결정
            if output_dir:
                # 사용자가 지정한 디렉토리 사용
                base_dir = output_dir
            else:
                # 자동으로 클라이언트 작업 디렉토리 감지
                base_dir = self._get_client_work_dir()
            
            # SpecGate 루트 및 data 폴더 생성 (중복 방지 정규화)
            norm_base = os.path.normpath(base_dir)
            marker = os.path.join("SpecGate", "data")
            if marker in norm_base:
                # base_dir가 이미 SpecGate/data 포함 → 그 경로를 data_dir로 사용
                before, _sep, _after = norm_base.partition(marker)
                specgate_root = os.path.join(before, "SpecGate")
                data_dir = os.path.join(specgate_root, "data")
            else:
                # 프로젝트 루트로 간주하여 SpecGate/data 생성
                specgate_root = os.path.join(norm_base, "SpecGate")
                data_dir = os.path.join(specgate_root, "data")
            html_files_dir = os.path.join(data_dir, "html_files")
            
            # data 폴더가 없으면 생성
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
                self.logger.info(f"data 폴더 생성: {data_dir}")
            
            # HTML 파일 저장 디렉토리 (직접 html_files 하위에 저장)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_dir = html_files_dir
            os.makedirs(html_dir, exist_ok=True)
            
            html_files = []
            for i, doc in enumerate(documents):
                if "html_content" in doc:
                    # 파일명 생성 (제목 기반)
                    title = doc.get("title") or "document"
                    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_title = safe_title.replace(' ', '_') or "document"
                    
                    # 동일 제목 기존 파일 제거 후 타임스탬프 포함 파일명 저장
                    # 예: {제목정규화}_YYYYMMDD_HHMMSS.html
                    # 중복 처리: {제목정규화}_*.html 삭제
                    import glob, re
                    pattern = os.path.join(html_dir, f"{safe_title}_*.html")
                    ts_regex = re.compile(rf"^{re.escape(safe_title)}_\d{{8}}_\d{{6}}\.html$")
                    for old_path in glob.glob(pattern):
                        base = os.path.basename(old_path)
                        if not ts_regex.match(base):
                            continue
                        try:
                            os.remove(old_path)
                            self.logger.info(f"기존 HTML 파일 삭제(중복 처리): {old_path}")
                        except Exception as _e:
                            self.logger.warning(f"기존 HTML 파일 삭제 실패: {old_path} ({_e})")

                    filename = f"{safe_title}_{timestamp}.html"
                    filepath = os.path.join(html_dir, filename)
                    
                    # HTML 파일 저장
                    if os.path.exists(filepath):
                        self.logger.info(f"기존 HTML 파일 대체: {filepath}")
                    async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                        await f.write(doc["html_content"])
                    
                    html_files.append(filepath)
                    self.logger.info(f"HTML 파일 저장: {filepath}")
            
            return html_files
            
        except Exception as e:
            self.logger.error(f"HTML 파일 저장 실패: {str(e)}")
            return []
    
    def _get_client_work_dir(self):
        """클라이언트 작업 디렉토리를 자동으로 감지"""
        import os
        
        # 1. 환경변수에서 클라이언트 작업 디렉토리 확인
        client_work_dir = os.environ.get('CLIENT_WORK_DIR')
        if client_work_dir and os.path.exists(client_work_dir):
            return client_work_dir
        
        # 2. MCP 서버가 실행되는 디렉토리의 상위 디렉토리 확인
        # (MCP 서버는 보통 development/mcp-server에서 실행되므로)
        current_dir = os.getcwd()
        if current_dir.endswith('/mcp-server'):
            parent_dir = os.path.dirname(current_dir)
            parent_parent_dir = os.path.dirname(parent_dir)
            # SpecGate 프로젝트 루트의 상위 디렉토리 확인
            if os.path.basename(parent_parent_dir) in ['클테코', 'Desktop']:
                return parent_parent_dir
        
        # 3. 기본값: 현재 작업 디렉토리
        return current_dir
