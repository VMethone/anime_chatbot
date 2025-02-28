import time


class Anime:
    def __init__(self, name, year):
        self.name = name
        self.year = year
        self.country = "ja"
        self.ani_type = "anime"
        self.moe_no_page = False
        self.housou_date = time.strptime(f"{year}.01.01", "%Y.%m.%d")  # 确保年份格式正确

    def __repr__(self):
        return f"Anime(名称='{self.name}', 年份={self.year}, 类型={self.ani_type}, " \
               f"国家='{self.country}', 页面存在={not self.moe_no_page})"

    def print_(self):
        print("{:^15}{:^15}{:^15}{:^15}{:^15}{:^15}{:^15}{:^15}{:^15}".format(
            self.name, self.country, self.year, self.ani_type, time.strftime("%Y-%m-%d", self.housou_date)
        ))

    def print_2(self):
        print("{:^10}{:^5}{:^10}{:^15}".format(
            str(self.year), str(self.season) if self.season != -1 else "未知", self.ani_type, self.name
        ))

    def print_3(self):
        print("{:^12}{:^3}{:^5}{:^5}{:^5}{:^8}{:^5}{:^15}{:^15}".format(
            time.strftime("%Y-%m-%d", self.housou_date),
            str(self.season) if self.season != -1 else "未知",
            self.country, self.ani_type, self.bangumi_id, self.episode, self.name[:14], self.jp_name[:14]
        ))
