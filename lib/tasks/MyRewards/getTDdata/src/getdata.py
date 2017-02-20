
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
name:getdata.py
purpose:get data from TD (sql file)
version:1.0 (20160722)
create date:20160722
author:Derek
note:
*/5 * * * * python getdata.py
'''
import jaydebeapi as jdbc
import os, time, json, datetime as de

USERNAME = "<account>"
PASSWORD = "<password>"

## define path of sql file and result data
pathofmyrewards= "/cms/jupyter/MyRewards/myrewards_writetable"
pathofCode = os.path.join(pathofmyrewards, "sql")
pathofJDBC = os.path.join(pathofmyrewards, "teradatajdbc")
sqlconfig = os.path.join(pathofCode, "sqlconfig.json")
logfile = os.path.join(pathofmyrewards, "log", time.strftime("%Y%m%d") + ".log")

## generate replacement mapping table
replace_dict = {}
this_month = de.date.today().replace(day = 1)
for i in range(13):
    last_month = this_month - de.timedelta(days = 1)
    last_month_str = last_month.strftime("%Y%m")
    replace_dict.setdefault("{MONTH" + "%02d" % (i + 1) + "}", last_month_str)
    this_month = last_month.replace(day = 1)

## excute sql from sql file
def exec_sql_file(sqlfile, sqlreplace, sqldict = replace_dict):
    ## read sql file text
    with open(sqlfile,'r') as sqlf:
        sqlscript = sqlf.read().decode('utf8').split("/* split */")
        sqlf.close()

    curs = conn.cursor()
    for i in range(len(sqlscript)):
        now_script = sqlscript[i]

        if sqlreplace == 'Y':
            for key, value in sqldict.items():
                now_script = now_script.replace(key, value)
            
        status = eval(str(now_script.split("/* ")[1].split(" */")[0]))
        
        if status["error"] == "pass":
            try :
                curs.execute(now_script)
            except :
                pass
        elif status["error"] == "alert":
            curs.execute(now_script)

    ## table count 
    tablename = "myrewards_" + sqlfile.replace(pathofCode + "/", "").replace(".sql", "").lower()[3:]
    curs.execute("select count(*) from fh_temp." + tablename)
    cnt_rows = curs.fetchall()

    curs.close()

    return cnt_rows

## define connection string to TD
## TD Jar file path /opt/teradatajdbc
conn = jdbc.connect('com.teradata.jdbc.TeraDriver',['jdbc:teradata://<database_ip>/tmode=ANSI,CLIENT_CHARSET=WINDOWS-950', USERNAME, PASSWORD],[os.path.join(pathofJDBC, 'terajdbc4.jar'),os.path.join(pathofJDBC, 'tdgssconfig.jar')])

## define lof file mode --> default :new
logfilemode = 'w'
if os.path.exists(logfile):
    ## if file exists : file mode =append
    logfilemode = 'a'

with open(logfile, logfilemode,0) as f_log:
    try:
        # start point
        f_log.write(time.strftime("%Y%m%d%H%M%S") +" PID:getdata.py Start ." + "\n")
        
        with open(sqlconfig, 'r') as f:
            ## read json:define which sqlpath ,enable-->Y/N ,sqltype-->E=insert/update, Q=select
            sqlfiles = json.load(f)
            for i in sqlfiles['sqlfiles']:
                if i['enable'] == 'Y':
                    ## print os.path.join(pathofCode, i['FileName'])
                    fname = os.path.join(pathofCode, i['FileName'])
                    ## start point:each sqlfile
                    f_log.write(time.strftime("%Y%m%d%H%M%S") + " Starting:" + fname + "\n")
                    f_log.write(time.strftime("%Y%m%d%H%M%S") + " Finished:" + fname + ":" + str(exec_sql_file(fname, i['replace'])) + "\n")
    except Exception, e:
        ## print "ERROR" + str(e)
        ## error message
        f_log.write(time.strftime("%Y%m%d%H%M%S") +" PID:getdata.py Error:" + str(e) + "\n")
    finally:
        f_log.write(time.strftime("%Y%m%d%H%M%S") +" PID:getdata.py Ends ." + "\n")

conn.close()
