import mysql.connector
from mysql.connector import Error
import configparser
import os
from datetime import datetime
from ThreadExecutor import ThreadExecutor

class PersonTransaction:
    config = configparser.ConfigParser()
    url = 'C:\\config.txt'
    assert os.path.exists(url)
    config.read(url)
    userName = config.get('configuration','userName').strip('"')
    userPassword = config.get('configuration','password').strip('"')
    hostURL = config.get('configuration','host').strip('"')
    dbName = config.get('configuration','database').strip('"')

    #TODO check why having global keyword is necessary
    global th
    th = ThreadExecutor.instance()

    def createLaborerTask(self,laborer):
        connection = mysql.connector.connect(host=self.hostURL,
                                    database=self.dbName,
                                    user=self.userName,
                                    password=self.userPassword)
        try:
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                statement = "Insert into karamdb.laborer"
                colNames = "(laborer_id,parent_id, first_name, last_name, gender, phone_number, address,adhar_card_number,adhar_card_status,pan_card,skill,active_ind,preferred_job_location)"
                colValues = "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                sql = statement+colNames+colValues
                val = (laborer.getLaborerId(),laborer.getParentId(),laborer.getFirstname(),laborer.getLastname(),laborer.getGender(),laborer.getPhoneNumber(),laborer.getAddress(),laborer.getAadharNo(),laborer.getAadharStatus(),laborer.getPanCard(),laborer.getSkill(),laborer.getActiveInd(),laborer.getPrefLoc())
                cursor.execute(sql,val)
                connection.commit()

                skills = laborer.getSkill().split(",")
                # Insert into skill table
                for skill in skills:
                    #TODO refactor this code to use select only once
                    sql = "select count(name) from skills where name=(%s)"
                    val = (skill,)
                    cursor.execute(sql,val)
                    res = cursor.fetchone()
                    if int(res[0]) == 0:
                        sql = "Insert into karamdb.skills (name,description) VALUES (%s,%s)"
                        val = (skill,"")
                        cursor.execute(sql,val)
                        connection.commit()

                    sql = "select name from skills where name=(%s)"
                    val = (skill,)
                    cursor.execute(sql,val)
                    res = cursor.fetchone()
                    skillName = res[0]
                    sql = "Insert into karamdb.laborerSkillRelation (laborer_id, skill_name) VALUES (%s,%s)"
                    val = (laborer.getLaborerId(), skillName)
                    cursor.execute(sql,val)
                    connection.commit()

                locations = laborer.getPrefLoc().split(",")
                # Insert into skill table
                for loc in locations:
                    #TODO refactor this code to use select only once
                    sql = "select count(*) from preferredJobLocation where STATE= %s and city = %s and district = %s"
                    val = (loc, loc, loc)
                    cursor.execute(sql,val)
                    res = cursor.fetchone()
                    if int(res[0]) == 0:
                        sql = "Insert into karamdb.preferredJobLocation (STATE,CITY,district) VALUES (%s,%s,%s)"
                        val = (loc,loc,loc)
                        cursor.execute(sql,val)
                        connection.commit()

                    sql = "select id from preferredJobLocation where STATE= %s and city = %s and district = %s"
                    val = (loc, loc, loc)
                    cursor.execute(sql,val)
                    res = cursor.fetchone()
                    locId = int(res[0])
                    sql = "Insert into karamdb.laborerPreferredLocationRelation (laborer_id, location_id) VALUES (%s,%s)"
                    val = (laborer.getLaborerId(), locId)
                    cursor.execute(sql,val)
                    connection.commit()

                print("Inserted successfully in laborer table")
                return "SUCCESS"

        except Error as e:
            print("Error while inserting into laborer, skill, laborerSkillRelation  table", e)
            return str(e)
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")


    def createLaborer(self,laborer):
        future = th.executor.submit(self.createLaborerTask,laborer)
        return future.result()

    def updateLaborerTask(self,laborer):
        connection = mysql.connector.connect(host=self.hostURL,
                                            database=self.dbName,
                                            user=self.userName,
                                            password=self.userPassword)
        try:
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                sql = "update karamdb.laborer set "
                values = []
                if(laborer.getFirstname()):
                    sql+="first_name = %s,"
                    values.append(laborer.getFirstname())
                if(laborer.getLastname()):
                    sql+="last_name = %s,"
                    values.append(laborer.getLastname())
                if(laborer.getPhoneNumber()):
                    sql+="phone_number = %s,"
                    values.append(laborer.getPhoneNumber())
                if(laborer.getAddress()):
                    sql+="address = %s,"
                    values.append(laborer.getAddress())
                if(laborer.getAadharStatus()):
                    sql+="adhar_card_status = %s,"
                    values.append(laborer.getAadharStatus())
                if(laborer.getAadharNo()):
                    sql+="adhar_card_number = %s,"
                    values.append(laborer.getAadharNo())
                if(laborer.getPanCard()):
                    sql+="pan_card = %s,"
                    values.append(laborer.getPanCard())
                if(laborer.getSkill()):
                    sql+="skill = %s,"
                    values.append(laborer.getSkill())
                if(laborer.getActiveInd()):
                    sql+="active_ind = %s,"
                    values.append(laborer.getActiveInd())
                if(laborer.getPrefLoc()):
                    sql+="preferred_job_location = %s,"
                    values.append(laborer.getPrefLoc())

                sql=sql.rstrip(',')
                print(sql)
                print(values)
                cursor.execute(sql,values)
                connection.commit()
                print("Updated successfully laborer table for "+laborer.getLaborerId())
                return "SUCCESS"

        except Error as e:
            print("Error while connecting to MySQL", e)
            return str(e)
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

    def updateLaborer(self,laborer):
        future = th.executor.submit(self.updateLaborerTask,laborer)
        return future.result()

    def getAllLaborerTask(self, skills, locations):
        connection = mysql.connector.connect(host=self.hostURL,
                                             database=self.dbName,
                                             user=self.userName,
                                             password=self.userPassword)
        try:
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()

                sql = "select * from karamdb.laborer"
                if skills and not locations:
                    #TODO this is not good for scalability we need to have SkillEq,SkillLike,SkillIn operation in JSON Request
                    sql = "select * from karamdb.laborer where laborer_id in ("
                    sql = sql + "select laborer_id from laborerSkillRelation where"
                    print(skills)
                    skillNames = skills.split(',')
                    values = []
                    for skillName in skillNames:
                        sql = sql + " skill_name like %s " + "OR"
                        values.append("%"+skillName+"%")
                    sql = sql[:-2]
                    sql = sql + ")"
                    cursor.execute(sql, values)
                elif locations and not skills:
                    sql = "select * from karamdb.laborer where laborer_id in ("
                    sql = sql + "select laborer_id from laborerPreferredLocationRelation where  location_id in ("
                    sql = sql + "select id from preferredJobLocation where"
                    locationNames = locations.split(',')
                    values = []
                    for locationName in locationNames:
                        sql = sql + " state like %s " + "OR"
                        values.append("%"+locationName+"%")
                    sql = sql[:-2]
                    sql = sql + "))"
                    cursor.execute(sql, values)
                elif locations and skills:
                    # TODO make above code modular so that it can be resused for this case
                    sql = sql + " where preferred_job_location in ({list})".format(list=','.join(['%s']*len(locations)))
                    sql = sql + " and skill in ({list})".format(list=','.join(['%s']*len(skills)))
                    values = []
                    for loc in locations:
                        values.append(loc)
                    for skill in skills:
                        values.append(skill)
                    cursor.execute(sql, values)
                else:
                    cursor.execute(sql)

                row_headers=[x[0] for x in cursor.description]
                rec = cursor.fetchall()
                json_data=[]
                for res in rec:
                    json_data.append(dict(zip(row_headers,res)))
                return json_data
        except Error as e:
            print("Error while connecting to MySQL", e)
            return str(e)
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

    def getAllLaborer(self, skills, locations):
        future = th.executor.submit(self.getAllLaborerTask, skills, locations)
        return future.result()

    def getFriendOfLaborerTask(self, parentId):
        connection = mysql.connector.connect(host=self.hostURL,
                                             database=self.dbName,
                                             user=self.userName,
                                             password=self.userPassword)
        try:
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                sql = "SELECT * FROM karamdb.laborer where parent_id = '"+parentId+"'"
                cursor.execute(sql)

                row_headers=[x[0] for x in cursor.description]
                rec = cursor.fetchall()
                json_data=[]
                for res in rec:
                    json_data.append(dict(zip(row_headers,res)))
                return json_data
        except Error as e:
            print("Error while connecting to MySQL", e)
            return str(e)
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

    def getFriendOfLaborer(self, parentId):
        future = th.executor.submit(self.getFriendOfLaborerTask, parentId)
        return future.result()

    def createContractorTask(self,contractor):
        connection = mysql.connector.connect(host=self.hostURL,
                                    database=self.dbName,
                                    user=self.userName,
                                    password=self.userPassword)
        try:
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                statement = "Insert into karamdb.contractor"
                colNames = "(contractor_id,parent_id, first_name, last_name, gender, phone_number, address,adhar_card_number,adhar_card_status,pan_card,skill,active_ind,preferred_job_location)"
                colValues = "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                sql = statement+colNames+colValues
                # TODO how to make it multiline
                val = (contractor.getContractorId(),contractor.getParentId(),contractor.getFirstname(),contractor.getLastname(),contractor.getGender(),contractor.getPhoneNumber(),contractor.getAddress(),contractor.getAadharNo(),contractor.getAadharStatus(),contractor.getPanCard(),contractor.getSkill(),contractor.getActiveInd(),contractor.getPrefLoc())
                cursor.execute(sql,val)
                connection.commit()
                print("Inserted successfully in contractor table")
                return "SUCCESS"

        except Error as e:
            print("Error while inserting into contractor table", e)
            return str(e)
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

    # TODO Update rest of sql functions like create, they are referring to old table schema
    def createContractor(self,contractor):
        future = th.executor.submit(self.createContractorTask,contractor)
        return future.result()

    def updateContractorTask(self,contractor):
        connection = mysql.connector.connect(host=self.hostURL,
                                            database=self.dbName,
                                            user=self.userName,
                                            password=self.userPassword)
        try:
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                sql = "update karamdb.contractor set "
                values = []
                if(contractor.getFirstname()):
                    sql+="first_name = %s,"
                    values.append(contractor.getFirstname())
                if(contractor.getLastname()):
                    sql+="last_name = %s,"
                    values.append(contractor.getLastname())
                if(contractor.getPhoneNumber()):
                    sql+="phone_number = %s,"
                    values.append(contractor.getPhoneNumber())
                if(contractor.getAddress()):
                    sql+="address = %s,"
                    values.append(contractor.getAddress())
                if(contractor.getAadharStatus()):
                    sql+="adhar_card_status = %s,"
                    values.append(contractor.getAadharStatus())
                if(contractor.getAadharNo()):
                    sql+="adhar_card_number = %s,"
                    values.append(contractor.getAadharNo())
                if(contractor.getPanCard()):
                    sql+="pan_card = %s,"
                    values.append(contractor.getPanCard())
                if(contractor.getSkill()):
                    sql+="skill = %s,"
                    values.append(contractor.getSkill())
                if(contractor.getActiveInd()):
                    sql+="active_ind = %s,"
                    values.append(contractor.getActiveInd())
                if(contractor.getPrefLoc()):
                    sql+="preferred_job_location = %s,"
                    values.append(contractor.getPrefLoc())

                sql=sql.rstrip(',')
                cursor.execute(sql, values)
                connection.commit()
                print("Updated successfully contractor table for "+contractor.getContractorId())
                return "SUCCESS"

        except Error as e:
            print("Error while connecting to MySQL", e)
            return str(e)
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

    def updateContractor(self,contractor):
        future = th.executor.submit(self.updateContractorTask,contractor)
        return future.result()

    def getAllContractorTask(self):
        connection = mysql.connector.connect(host=self.hostURL,
                                             database=self.dbName,
                                             user=self.userName,
                                             password=self.userPassword)
        try:
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                sql = "SELECT * FROM karamdb.contractor"
                cursor.execute(sql)
                row_headers=[x[0] for x in cursor.description]
                rec = cursor.fetchall()
                json_data=[]
                for res in rec:
                    json_data.append(dict(zip(row_headers,res)))
                return json_data
        except Error as e:
            print("Error while connecting to MySQL", e)
            return str(e)
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

    def getAllContractor(self):
        future = th.executor.submit(self.getAllContractorTask)
        return future.result()

    def createUserTask(self,user):
        connection = mysql.connector.connect(host=self.hostURL,
                                    database=self.dbName,
                                    user=self.userName,
                                    password=self.userPassword)
        try:
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                statement = "Insert into karamdb.user"
                colNames = "(role_type,user_name,password_hash)"
                colValues = "VALUES (%s,%s,%s)"
                sql = statement+colNames+colValues
                val = (user.getRoleType(),user.getUserName(),user.getPasswordHash())
                cursor.execute(sql,val)
                connection.commit()
                print("Inserted successfully in user table")
                return "SUCCESS"

        except Error as e:
            print("Error while inserting into user table", e)
            return str(e)
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

    def createJob(self,job):
        future = th.executor.submit(self.createJobTask,job)
        return future.result()

    def createJobTask(self,job):
        connection = mysql.connector.connect(host=self.hostURL,
                                    database=self.dbName,
                                    user=self.userName,
                                    password=self.userPassword)
        try:
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                statement = "Insert into karamdb.job"
                colNames = "(labour_id,contractor_id,active_ind)"
                colValues = "VALUES (%s,%s,%s)"
                sql = statement+colNames+colValues
                val = (job.getLaborerId(),job.getContractorId(),job.getActiveInd())
                cursor.execute(sql,val)
                connection.commit()
                print("Inserted successfully in job table")
                return "SUCCESS"

        except Error as e:
            print("Error while inserting into user table", e)
            return str(e)
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

    def createUser(self,user):
        future = th.executor.submit(self.createUserTask,user)
        return future.result()

    def getNewUserId(self):
        connection = mysql.connector.connect(host=self.hostURL,
                                             database=self.dbName,
                                             user=self.userName,
                                             password=self.userPassword)
        try:
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                sql = "SELECT max(user_id) FROM karamdb.user"
                cursor.execute(sql)
                result = cursor.fetchone()
                return int(result[0])
        except Error as e:
            print("Error while connecting to MySQL", e)
            return str(e)
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

    def deleteById(id):
        future = th.executor.submit(deleteByIdTask,id)
        return future.result()

    def deleteByIdTask(id):
        try:
            connection = mysql.connector.connect(host=hostURL,
                                                database=dbName,
                                                user=userName,
                                                password=userPassword)
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                sql = "delete from karamdb.person where person_id = %s"
                val = (id,)
                cursor.execute(sql,val)
                connection.commit()
                record = cursor.fetchone()
                print("You're connected to database: ", record)

        except Error as e:
            print("Error while connecting to MySQL", e)
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

    def getAllPersonById(id):
        future = th.executor.submit(getPersonByIdTask,id)
        return future.result()

    def getPersonByIdTask(id):
        try:
            connection = mysql.connector.connect(host=hostURL,
                                                 database=dbName,
                                                 user=userName,
                                                 password=userPassword)
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                sql = "select * from karamdb.person where person_id = %s"
                val = (id,)
                cursor.execute(sql,val)
                rec = cursor.fetchall()
                result = list()
                for x in rec:
                    result.append(x)
                return result
        except Error as e:
            print("Error while connecting to MySQL", e)
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

#print(createLaborer("DEF","","R","P","M","9819888888","address","adharNo123","Y","panCardNo123","skill123","Y","DELHI"))
