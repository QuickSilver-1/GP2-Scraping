from dotenv import load_dotenv
import os
import yaml

class MapParser:
    base_url: str
    api_key: str

class HouseScrapper:
    base_url: str
    user_agent: str
    domain: str
    
class Logger:
    level: str
    output_file: str
    
class Excel:
    raw_path: str
    temp_path: str
    processed_path: str
    raw_sheet_name: str
    temp_sheet_name: str
    processed_sheet_name: str

class Config:
    parser: MapParser = MapParser()
    scrapper: HouseScrapper = HouseScrapper()
    logger: Logger = Logger()
    excel: Excel = Excel()

    def __init__(self, env_path: str = "./.env", yaml_path: str = "./config.yaml"):        
        load_dotenv(env_path)
        self.parser.api_key = os.getenv("API_KEY")
        
        yamlData = yaml.safe_load(open(yaml_path, "r"))
        self.parser.base_url = yamlData["parser"]["base_url"]
        
        self.scrapper.base_url = yamlData["scrapper"]["base_url"]
        self.scrapper.user_agent = yamlData["scrapper"]["user_agent"]
        self.scrapper.domain = yamlData["scrapper"]["domain"]
        
        self.logger.level = yamlData["logger"]["level"]
        self.logger.output_file = yamlData["logger"]["output_file"]
        
        self.excel.raw_path = yamlData["excel"]["raw_path"]
        self.excel.temp_path = yamlData["excel"]["temp_path"]
        self.excel.processed_path = yamlData["excel"]["processed_path"]
        self.excel.raw_sheet_name = yamlData["excel"]["raw_sheet_name"]
        self.excel.temp_sheet_name = yamlData["excel"]["temp_sheet_name"]
        self.excel.processed_sheet_name = yamlData["excel"]["processed_sheet_name"]
        