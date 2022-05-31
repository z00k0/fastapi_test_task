def resp_to_dict(row):
    id_1 = row._mapping['id_1']
    dev_id = row._mapping['dev_id']
    dev_type = row._mapping['dev_type']
    _device = {'id': id_1, 'dev_id': dev_id, 'dev_type': dev_type}
    _id = row._mapping['id']
    comment = row._mapping['comment']
    _endpoint = {'device_id': _device, 'id': _id, 'comment': comment}

    return _endpoint


def is_anagram(str_1: str, str_2: str) -> bool:
    return sorted(str_1) == sorted(str_2)
