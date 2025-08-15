import os
import sys
from typing import Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Raised when required configuration is missing"""
    pass

class Config:
    """Application configuration with validation"""
    
    def __init__(self):
        self.validate_environment()
    
    @property
    def database_url(self) -> str:
        """Get database URL with validation"""
        url = os.getenv("DATABASE_URL")
        if not url:
            raise ConfigError("DATABASE_URL environment variable is required")
        return url
    
    @property
    def secret_key(self) -> str:
        """Get JWT secret key with validation"""
        key = os.getenv("SECRET_KEY")
        if not key:
            raise ConfigError("SECRET_KEY environment variable is required")
        if len(key) < 32:
            raise ConfigError("SECRET_KEY must be at least 32 characters long")
        return key
    
    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key with validation"""
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ConfigError("OPENAI_API_KEY environment variable is required")
        if not key.startswith("sk-"):
            raise ConfigError("OPENAI_API_KEY must be a valid OpenAI API key")
        return key
    
    @property
    def stripe_secret_key(self) -> str:
        """Get Stripe secret key with validation"""
        key = os.getenv("STRIPE_SECRET_KEY")
        if not key:
            raise ConfigError("STRIPE_SECRET_KEY environment variable is required")
        if not key.startswith("sk_"):
            raise ConfigError("STRIPE_SECRET_KEY must be a valid Stripe secret key")
        return key
    
    @property
    def stripe_publishable_key(self) -> Optional[str]:
        """Get Stripe publishable key (optional for backend)"""
        return os.getenv("STRIPE_PUBLISHABLE_KEY")
    
    @property
    def stripe_webhook_secret(self) -> Optional[str]:
        """Get Stripe webhook secret (optional, needed for webhooks)"""
        return os.getenv("STRIPE_WEBHOOK_SECRET")
    
    @property
    def yelp_api_key(self) -> Optional[str]:
        """Get Yelp API key (optional, has fallback)"""
        return os.getenv("YELP_API_KEY")
    
    @property
    def frontend_url(self) -> str:
        """Get frontend URL for CORS"""
        return os.getenv("FRONTEND_URL", "https://useleadnest.com")
    
    @property
    def redis_url(self) -> str:
        """Get Redis URL for rate limiting"""
        return os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    @property
    def environment(self) -> str:
        """Get environment (development, production, test)"""
        return os.getenv("ENVIRONMENT", "development")
    
    @property
    def algorithm(self) -> str:
        """Get JWT algorithm"""
        return os.getenv("ALGORITHM", "HS256")
    
    @property
    def access_token_expire_minutes(self) -> int:
        """Get JWT token expiration time"""
        return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    def validate_environment(self) -> None:
        """Validate all required environment variables"""
        required_vars = [
            "DATABASE_URL",
            "SECRET_KEY", 
            "OPENAI_API_KEY",
            "STRIPE_SECRET_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ConfigError(error_msg)
        
        # Validate specific formats
        try:
            self.secret_key  # Validates length
            self.openai_api_key  # Validates format
            self.stripe_secret_key  # Validates format
        except ConfigError as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            raise
        
        logger.info("✅ All required environment variables validated successfully")
    
    def get_cors_origins(self) -> list:
        """Get CORS origins based on environment"""
        if self.environment == "production":
            return [
                self.frontend_url,
                "https://*.vercel.app",
                "https://*.onrender.com"
            ]
        else:
            return [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                self.frontend_url
            ]
    
    def log_configuration(self) -> None:
        """Log configuration status (without sensitive data)"""
        logger.info("🔧 Configuration Status:")
        logger.info(f"  Environment: {self.environment}")
        logger.info(f"  Database: {'✅ Connected' if self.database_url else '❌ Missing'}")
        logger.info(f"  OpenAI API: {'✅ Configured' if self.openai_api_key else '❌ Missing'}")
        logger.info(f"  Stripe API: {'✅ Configured' if self.stripe_secret_key else '❌ Missing'}")
        logger.info(f"  Yelp API: {'✅ Configured' if self.yelp_api_key else '⚠️  Using Mock Data'}")
        logger.info(f"  Frontend URL: {self.frontend_url}")

# Global configuration instance
try:
    config = Config()
    if config.environment != "test":
        config.log_configuration()
except ConfigError as e:
    logger.error(f"❌ Configuration Error: {str(e)}")
    if os.getenv("ENVIRONMENT") != "test":
        print(f"\n❌ Configuration Error: {str(e)}")
        print("\n🔧 Please check your .env file and ensure all required variables are set.")
        print("   See .env.example for the required format.")
        sys.exit(1)
