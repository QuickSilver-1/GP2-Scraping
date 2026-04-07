from dotenv import load_dotenv
import os
import yaml


class YandexApi:
    geocode_url: str
    geocode_api_key: str
    routing_url: str
    routing_api_key: str
    overpass_url: str


class AqicnApi:
    base_url: str
    api_key: str


class DaDataApi:
    base_url: str
    api_key: str


class Parser:
    yandex_api: YandexApi
    aqicn_api: AqicnApi
    dadata_api: DaDataApi

    def __init__(self):
        self.yandex_api = YandexApi()
        self.aqicn_api = AqicnApi()
        self.dadata_api = DaDataApi()


class HouseScrapper:
    base_url: str
    user_agent: str


class Logger:
    level: str
    output_file: str


class Config:
    scrapper: HouseScrapper = HouseScrapper()
    logger: Logger = Logger()
    parser: Parser = Parser()

    def __init__(self, env_path: str = "./.env", yaml_path: str = "./config.yaml"):
        load_dotenv(env_path)
        self.parser.yandex_api.geocode_api_key = os.getenv("YANDEX_GEOCODE_API_KEY")
        self.parser.yandex_api.routing_api_key = os.getenv("YANDEX_ROUTING_API_KEY")
        self.parser.aqicn_api.api_key = os.getenv("AQICN_API_KEY")
        self.parser.dadata_api.api_key = os.getenv("DADATA_API_KEY")

        yamlData = yaml.safe_load(open(yaml_path, "r"))
        self.scrapper.base_url = yamlData["scrapper"]["base_url"]
        self.scrapper.user_agent = yamlData["scrapper"]["user_agent"]

        self.logger.level = yamlData["logger"]["level"]
        self.logger.output_file = yamlData["logger"]["output_file"]

        self.parser.yandex_api.geocode_url = yamlData["parser"]["yandex_geocode_url"]
        self.parser.yandex_api.routing_url = yamlData["parser"]["yandex_routing_url"]
        self.parser.yandex_api.overpass_url = yamlData["parser"]["overpass_url"]
        self.parser.aqicn_api.base_url = yamlData["parser"]["aqicn_url"]
        self.parser.dadata_api.base_url = yamlData["parser"]["dadata_url"]
