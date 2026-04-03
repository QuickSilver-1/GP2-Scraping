from dotenv import load_dotenv
import os
import yaml

class MapParser:
    base_url: str
    api_key: str

class HouseScrapper:
    base_url: str
    user_agent: str
    
class Logger:
    level: str
    output_file: str

class Config:
    parser: MapParser = MapParser()
    scrapper: HouseScrapper = HouseScrapper()
    logger: Logger = Logger()

    def __init__(self, env_path: str = "./.env", yaml_path: str = "./config.yaml"):        
        load_dotenv(env_path)
        self.parser.api_key = os.getenv("API_KEY")
        
        yamlData = yaml.safe_load(open(yaml_path, "r"))
        self.parser.base_url = yamlData["parser"]["base_url"]
        
        self.scrapper.base_url = yamlData["scrapper"]["base_url"]
        self.scrapper.user_agent = yamlData["scrapper"]["user_agent"]
        
        self.logger.level = yamlData["logger"]["level"]
        self.logger.output_file = yamlData["logger"]["output_file"]
        