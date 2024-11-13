from utils import File
from utils import TSVFile as TSVFileOld


class TSVFile(TSVFileOld):
    def write(self, d_list):

        BASE_KEY_LIST = [
            "entity_id",
            "timestamp",
            "electors",
            "polled",
            "valid",
            "rejected",
        ]

        k_to_v_sum = {}
        for d in d_list:
            for k, v in d.items():
                if k and k not in BASE_KEY_LIST:
                    if k not in k_to_v_sum:
                        k_to_v_sum[k] = 0
                    k_to_v_sum[k] += v
        value_key_list = [
            k
            for k, v in sorted(
                k_to_v_sum.items(), key=lambda x: x[1], reverse=True
            )
        ]

        key_list = BASE_KEY_LIST + value_key_list
        d_list = [{k: d.get(k, 0) for k in key_list} for d in d_list]
        d_list.sort(key=lambda x: x["entity_id"])

        super().write(d_list)
        text_file = File(self.path)
        lines = text_file.read_lines()
        lines = [line for line in lines if line]
        text_file.write_lines(lines)
