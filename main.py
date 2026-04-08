from multiprocessing import Process, process
import multiprocessing
import pandas as pd
from pathlib import Path
from src import api_collector, config, logger, web_scrapper
import time
from src.api_collector import ApiCollector
from src.excel_handler import ExcelHandler, DataSetType

def main() -> None:
    cfg = config.Config()
    
    print("Добрый день, это наш проект ГП2 по СМАДИМО!")
    print("Это инструмент для сбора и обогащения информации о продающихся в Москве квартирах")
    
    print("ЭТАП 1. Сбор данных с сайта ДомКлик.ру")
    print("Для работы этого этапа необходимо запустить Chrome в режиме разработки (см. README.md)")
    print("Хотите запустить этот этап?")
    print("Y/n")
    part1 = input()
    if part1 == "Y":
        queries = [
            ("Россия, Москва, Западный административный округ", 9222),
            ("Северный административный округ, Москва", 9223),
            ("Южный административный округ, Москва", 9224),
            ("Россия, Москва, Северо-Восточный административный округ", 9225),
            ("Юго-Западный административный округ, Москва", 9226),
            # ("Россия, Москва, Северо-Западный административный округ", 9227),
            # ("Юго-Восточный административный округ, Москва", 9228),
            # ("Центральный административный округ, Москва", 9229),
            # ("Восточный административный округ, Москва", 9230)
        ]
        
        processes = []
        for i, query in enumerate(queries):
            query_text = query[0]
            port = query[1]
            excel_path = cfg.excel.raw_path + f"{i+2}.xlsx"
            
            p = Process(
                target=mutiprocessing_scrape,
                args=(
                    query_text,
                    port,
                    excel_path,
                    cfg.scrapper,
                    cfg.logger.level,
                    cfg.logger.output_file,
                    cfg.excel
                )
            )
            p.start()
            processes.append(p)
            time.sleep(15)
            
            time.sleep(60*60*10)
            for p in processes:
                p.terminate()
            
            print("Сбор данных успешно завершен")
        
    print("Этап 2. Слияние собранных данных в единый датасет")
    print("Хотите запустить этот этап?")
    print("Y/n")
    part2 = input()
    if part2 == "Y":
        folder = Path("/".join(cfg.excel.raw_path.split("/")[:-1]))
        files = list(folder.glob('*.xlsx'))

        df = pd.DataFrame()
        for file in files:
            df = pd.concat([df, pd.read_excel(file)])
            
        address = df.columns[0]
        S = df.columns[1]
        df = df.drop_duplicates(subset=[address, S], keep="last")
        excel_handler = ExcelHandler(cfg.excel)
        excel_handler.save(DataSetType.TEMP, df)
        
        print("Объединение данных успешно завершено")
        
    log = logger.get_logger(cfg.logger.level, cfg.logger.output_file)
    excel_handler = ExcelHandler(cfg.excel)
    
    print("Этап 3. Сбор дополнительных данных через API")
    print("Хотите запустить этот этап?")
    print("Y/n")
    part3 = input()
    if part3 == "Y":
        collector = ApiCollector(cfg.parser, log, excel_handler)
        collector.all_api_collect()
        
    print("Полный сбор данных успешно завершен. Дальнейшая работа с датасетом в ноутбуке")
    print("Спасибо за использование! Поставьте 10 плиз")
    
def mutiprocessing_scrape(query_text, area_id, excel_path, scrapper_config, log_level, log_output, excel_config):    
    log = logger.get_logger(log_level, log_output)
    log.bind(app="GP2")
    log.info(f"Starting scrape for: {query_text}")
    
    excel_handler = web_scrapper.ExcelHandler(excel_config)
    excel_handler.set_raw_path(excel_path)
    
    scraper = web_scrapper.SeleniumScraper(scrapper_config, log, excel_handler, area_id)
    scraper.scrape(query_text)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()