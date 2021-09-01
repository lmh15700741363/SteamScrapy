# coding=utf-8
"""
使用DBUtils数据库连接池中的连接，操作数据库
OperationalError: (2006, ‘MySQL server has gone away’)
"""
from datetime import date
from collections import Iterable
from dbutils.pooled_db import PooledDB
from . import log
import pymysql
import re


class MysqlClient(object):
    def __init__(self, mincached=5, maxcached=15, maxshared=10, maxconnections=200, blocking=True, maxusage=100,
                 setsession=None, reset=True):
        """

        :param mincached:连接池中空闲连接的初始数量
        :param maxcached:连接池中空闲连接的最大数量
        :param maxshared:共享连接的最大数量
        :param maxconnections:创建连接池的最大数量
        :param blocking:超过最大连接数量时候的表现，为True等待连接数量下降，为false直接报错处理
        :param maxusage:单个连接的最大重复使用次数
        :param setsession:optional list of SQL commands that may serve to prepare
            the session, e.g. ["set datestyle to ...", "set time zone ..."]
        :param reset:how connections should be reset when returned to the pool
            (False or None to rollback transcations started with begin(),
            True to always issue a rollback for safety's sake)
        :param host:数据库ip地址
        :param port:数据库端口
        :param db:库名
        :param user:用户名
        :param passwd:密码
        :param charset:字符编码
        """

        dbInfo = self.__class__.get_dbinfo()
        self.__pool = PooledDB (pymysql, mincached, maxcached, maxshared, maxconnections,
                               blocking, maxusage, setsession, reset,
                               host=dbInfo['host'], port=dbInfo['port'], db=dbInfo['db'],
                               user=dbInfo['user'], passwd=dbInfo['passwd'],
                               charset=dbInfo.get('chartset') if dbInfo.get('chartset') else 'utf8',
                               cursorclass=pymysql.cursors.DictCursor
                               )

    @staticmethod
    def get_dbinfo():
        """
        根据连接名称获取数据库连接信息
        :param connectionName: 数据库连接名称
        :return:
        """
        dbInfo = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'passwd': 'your passwd',
            'db': 'temp'
        }
        return dbInfo

    def __get_conn(self, *args, **kwargs):
        # 如果传参中包含了数据库连接，则不从连接池重新取
        conn = kwargs.get('conn')
        cur = kwargs.get('cur')
        if not conn or not cur:
            conn = self.__pool.connection()
            cur = conn.cursor()
        return conn, cur

    # def close(self):
    #     try:
    #         self._cursor.close()
    #         self._conn.close()
    #     except Exception as e:
    #         print(e)
    #

    @staticmethod
    def __dict_datetime_obj_to_str(result_dict):
        """把字典里面的datatime对象转成字符串，使json转换不出错"""
        if result_dict:
            result_replace = {k: v.__str__() for k, v in result_dict.items() if isinstance(v, date)}
            result_dict.update(result_replace)
        return result_dict

    def raw(self, sql, data=(), *args, **kwargs):
        """执行原生SQL语句"""
        conn, cur = self.__get_conn(*args, **kwargs)
        try:
            cur.execute(sql, data)
            conn.commit()
        except Exception as e:
            log.logger.warning(f"{e}:,sql:{sql}")
            conn.rollback()
        return conn, cur

    def _raw_many(self, sql, data=None, *args, **kwargs):
        """执行多行数据的增、删、改语句"""
        if not data:
            log.logger.warning("data is null, sql:" + sql)
            return

        conn, cur = self.__get_conn(*args, **kwargs)

        table_name = re.search('insert into (.*?) .*', sql, re.M|re.I).group(1)
        try:
            cur.executemany(sql, data)
            conn.commit()
            log.logger.info(table_name + " data updated successfully")
        except Exception as e:
            log.logger.warning(f"{table_name}--{e}")
            conn.rollback()

    def select(self, sql, param=(), *args, **kwargs):
        """
        查询多个结果
        :param sql: sql语句
        :param param: sql参数
        :return: 结果数量和查询结果集
        """
        conn, cur = self.raw(sql, param, *args, **kwargs)
        result = cur.fetchall()
        """:type result:list"""
        result = [self.__dict_datetime_obj_to_str(row_dict) for row_dict in result]
        # print(result)
        return result

    def insert_many(self, table_name: str, columns: Iterable, data: Iterable, *args,**kwargs):
        """执行对行数据插入方法"""
        sql = f"""
               insert into {table_name} ({','.join(columns)}) 
               values ({','.join(['%s' for i in range(len(columns))])})
               on duplicate key update {','.join([f'{n}=values({n})' for n in columns])} 
               """
        return self._raw_many(sql, data, *args, **kwargs)
