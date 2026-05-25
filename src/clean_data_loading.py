import pandas as pd
from sqlalchemy import create_engine
import time
import os

db_uri = 'mysql+pymysql://root:123456@localhost:3306/taobao_data?charset=utf8mb4'
engine = create_engine(db_uri)

file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'UserBehavior.csv.zip')
target_table = 'user_behavior_sample'
chunk_size = 500000
sample_fraction = 0.01

start_time = time.time()
total_inserted = 0


col_names = ['user_id', 'item_id', 'category_id', 'behavior_type', 'timestamp']


data_stream = pd.read_csv(
    file_path,
    chunksize=chunk_size,
    compression='zip',
    header=None,
    names=col_names,
    encoding='utf-8'
)

for i, chunk in enumerate(data_stream):
    sampled_chunk = chunk.sample(frac=sample_fraction, random_state=42)

    sampled_chunk = sampled_chunk.dropna()

    sampled_chunk = sampled_chunk.drop_duplicates(
        subset=['user_id', 'item_id', 'behavior_type', 'timestamp'],
        keep='first'
    )

    sampled_chunk['timestamp'] = pd.to_datetime(sampled_chunk['timestamp'], unit='s')

    if not sampled_chunk.empty:
        sampled_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=10000
        )
        total_inserted += len(sampled_chunk)


end_time = time.time()
print(f"最终抽取并清洗入库：{total_inserted} 条数据。")
print(f"总耗时: {(end_time - start_time) / 60:.2f} 分钟")