

##

import argparse, os, sqlite3 as sql3

##


pars = argparse.ArgumentParser(description='WAd V2.0 Python version')
pars.add_argument('-c', action='store_true', help='Get all your contact numbers')
pars.add_argument('-cn', action='store_true', help='Like -c but added more info')
pars.add_argument('-gid', action='store_true', help='Dump all the groups id')
pars.add_argument('-ga', metavar='gid', default=None, help='Get aditional info bout group admins')
pars.add_argument('-gn', metavar='gid', default=None, help='Get number of all member in group')
pars.add_argument('-gm', metavar='gid', default=None, help='Get list of members in group with aditional info')
pars.add_argument('-o', metavar='filename', default=None, help='Save output to a file')

arg = pars.parse_args()



dql = {
        'contact':{
            'dbname':'wa.db',
            'c':'select number from wa_contacts where is_whatsapp_user = "1" and number not like "%@s%" ',
            'cn':'select number, display_name, wa_name, status from wa_contacts where is_whatsapp_user = "1" and number not like "%@s%" '
            },
        'group':{
            'dbname':'msgstore.db',
            'gid':'select key_remote_jid, subject from chat_list where key_remote_jid like "%@g.us%" ',
            'ga':'select gjid, jid, creation, subject from group_participants, chat_list where admin != 0  and key_remote_jid like "%inislh%" and gjid like "%inislh%" and jid like "%@s%" ',
            'gm':'select jid, admin, subject from group_participants, chat_list where gjid like "%inislh%" and key_remote_jid like "%inislh%" '
            }
        }

def cpk():
    #
    wapkg = ['com.whatsapp', 'com.gbwhatsapp']
    cp = lambda pn: pn if ( os.path.exists(pn) ) else ""
    pdb = "".join( cp( '/data/data/'+i+'/databases/' ) for i in wapkg )
    if pdb == "":
        os.sys.exit('Cannot find WhatsApp package name.\nMakesure you install the application.')
    return pdb



def qe(db, que):
    #
    conn = sql3.connect(db)
    cur = conn.execute(que)
    return cur


def dc(pdb):
    #
    pdb += dql["contact"]["dbname"]
    dres = ""
    if arg.c:
        dres += "\n".join( n[0] for n in qe(pdb, dql["contact"]["c"] ) )
    elif arg.cn:
        for row in qe(pdb, dql["contact"]["cn"]):
            dres += "Display Name : %s\n"% row[1]
            dres += "WA Name      : %s\n" % row[2]
            dres += "Number       : %s\n"% row[0]
            dres += "Status       : %s\n\n"% row[3]
    return dres

def dg( pdb ):
    #
    from datetime import datetime as dt
    gid = arg.gm or arg.ga or arg.gn
    pdb += dql["group"]["dbname"]
    dres = ""
    if arg.gid:
        for row in qe( pdb, dql["group"]["gid"] ):
            dres += "Name    : %s\n"% row[1]
            dres += "GID     : %s\n\n"% row[0].split('-')[1].split('@')[0]
    elif arg.ga:
        dres0 = ""
        for row in qe( pdb, dql["group"]["ga"].replace("inislh", gid) ):
            an = row[1].split('@s')[0]
            anm = "".join( i[0] for i in qe(pdb.replace('msgstore', 'wa'), 'select wa_name from wa_contacts where jid like "%'+an+'%" ') )
            cg = row[0].split('-')[0]
            ct = str(dt.fromtimestamp(int(str(row[2])[:-3])))
            gn = row[3]
            dres0 += "Name   : %s\n"% anm
            dres0 += "Number : %s\n\n"% an
        dres += "Group name  : %s\n"% gn
        dres += "Created by  : %s\n"% cg
        dres += "Date create : %s\n\n"% ct
        dres += dres0
    elif arg.gm or arg.gn:
        ares = ""
        gnum = ""
        for row in qe( pdb, dql["group"]['gm'].replace('inislh', gid) ):
            num = row[0].split('@s')[0]
            if num == '':
                continue
            gnum += "%s\n"% num
            stsu = lambda : "( Admin )" if ( row[1] != 0 ) else ""
            for srow in qe(pdb.replace('msgstore', 'wa'), 'select wa_name, status from wa_contacts where jid like "%'+num+'%"'):
                nm = srow[0]
                psts = srow[1]
                ares += "Name    : %s %s\n"% (nm, stsu())
                ares += 'Number  : %s\n'% num
                ares += 'About   : %s\n\n'% psts
                break
            gn = row[2]
        dres += "Group name  : %s\n"% gn
        dres += "Description : %s\n"% "".join( i[0] for i in qe( pdb.replace('msgstore', 'wa'), 'select description from wa_group_descriptions where jid like "%'+gid+'%"' ) )
        dres +=  ares
    if arg.gn:
        return gnum
    else:
        return dres


def mutm():
    #
    db = cpk()
    result = dg( db ) or dc( db )
    if arg.o:
        open(arg.o, 'w').write(result.encode('utf-8'))
        print "Saved to %s"% arg.o
    else:
        print result

mutm()
