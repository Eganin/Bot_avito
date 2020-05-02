from typing import NamedTuple
from dataclasses import dataclass


class NamedTupleREC(NamedTuple):
    shop_id: int
    price: str


res = NamedTupleREC(40, '40000')
for i in res :
    print(i)
print(res[2])