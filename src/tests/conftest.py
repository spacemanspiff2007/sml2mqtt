import pytest


@pytest.fixture
def test_data_1():
    data = b'1B1B1B1B01010101760501188E6162006200726500000101760101070000000000000B000000000000000000000101636877007' \
           b'60501188E626200620072650000070177010B000000000000000000000172620165002EC3F47A77078181C78203FF0101010104' \
           b'45425A0177070100000009FF010101010B000000000000000000000177070100010800FF6401018001621E52FB690000000A7AC' \
           b'1BC170177070100010801FF0101621E52FB690000000A74B1EA770177070100010802FF0101621E52FB6900000000060FD1A001' \
           b'77070100020800FF6401018001621E52FB69000000000D19E1C00177070100100700FF0101621B52FE55000089D901770701002' \
           b'40700FF0101621B52FE55000020220177070100380700FF0101621B52FE5500000A9201770701004C0700FF0101621B52FE5500' \
           b'005F2501010163810200760501188E636200620072650000020171016325FC000000001B1B1B1B1A0356F5'

    yield data
