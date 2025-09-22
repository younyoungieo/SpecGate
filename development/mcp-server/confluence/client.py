"""
Confluence API 클라이언트
"""
import os
import logging
import aiohttp
from typing import Dict, Any, Optional


class ConfluenceAPIClient:
    """Confluence API 클라이언트"""
    
    def __init__(self):
        self.logger = logging.getLogger("specgate.confluence.client")
        self.domain = None
        self.email = None
        self.api_token = None
        self._validate_environment()
    
    def _validate_environment(self) -> bool:
        """Confluence 환경변수 검증"""
        required_vars = ["CONFLUENCE_DOMAIN", "CONFLUENCE_EMAIL", "CONFLUENCE_API_TOKEN"]
        
        self.logger.info(f"  전체 환경변수 개수: {len(os.environ)}")
        
        missing_vars = []
        for var in required_vars:
            value = os.getenv(var)
            if value:
                self.logger.info(f"  ✅ {var}: {value[:10]}...")
                setattr(self, var.lower().replace('confluence_', ''), value)
            else:
                self.logger.info(f"  ❌ {var}: Not set")
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.warning(f"⚠️ Missing required environment variables: {', '.join(missing_vars)}")
            self.logger.info("💡 Cursor에서 MCP 서버를 사용할 때는 mcp.json의 환경변수가 자동으로 전달됩니다.")
            self.logger.info("💡 직접 실행 시에는 환경변수를 설정하거나 기본값을 사용합니다.")
            
            # 기본값 설정 (개발/테스트용)
            self.domain = os.getenv("CONFLUENCE_DOMAIN", "your-domain.atlassian.net")
            self.email = os.getenv("CONFLUENCE_EMAIL", "your-email@example.com")
            self.api_token = os.getenv("CONFLUENCE_API_TOKEN", "ATATT3xFfGF...")
            
            self.logger.info("🔧 기본값으로 설정되었습니다 (개발/테스트용)")
            return True
        
        return True
    
    def is_configured(self) -> bool:
        """Confluence 클라이언트가 올바르게 구성되었는지 확인"""
        return bool(self.domain and self.email and self.api_token)
    
    async def search_content(self, cql: str, limit: int = 10) -> Dict[str, Any]:
        """Confluence API로 콘텐츠 검색"""
        url = f"https://{self.domain}/wiki/rest/api/content/search"
        
        params = {
            "cql": cql,
            "limit": limit,
            "expand": "body.storage,version,space,ancestors"
        }
        
        auth = aiohttp.BasicAuth(self.email, self.api_token)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, auth=auth) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"✅ Confluence API 호출 성공: {len(data.get('results', []))}개 문서")
                        return data
                    else:
                        error_text = await response.text()
                        self.logger.error(f"❌ Confluence API 호출 실패: {response.status} - {error_text}")
                        return {"error": f"API 호출 실패: {response.status}"}
        except Exception as e:
            self.logger.error(f"❌ Confluence API 호출 중 오류: {str(e)}")
            return {"error": f"API 호출 오류: {str(e)}"}
    
    def generate_cql_query(self, label: str, space_key: Optional[str] = None) -> str:
        """CQL 쿼리 생성"""
        if space_key:
            cql = f'label = "{label}" AND space = "{space_key}"'
        else:
            cql = f'label = "{label}"'
        
        self.logger.info(f"🔍 생성된 CQL 쿼리: {cql}")
        return cql
