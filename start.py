# -*- coding: utf-8 -*-
from lw_dm import MptdScreen
import os, sys, getopt, shelve

TEST = True

def usage():
    print """Options :
    -f          --fullscreen            Fullscreen
    -1          --one-player            Single player
    -n          --no-network            No networking (useless)
    -h          --help                  this help
    -s          --server                specify the server IP address
    -p          --port                  specify the port the server is listening on"""

def create_default_config(config_file):
    s = shelve.open(config_file)
    settings = {
        "server_ip"  : "localhost",
        "server_port": "8524",
        "fullscreen" : False,
        "solo"       : True
        }
    keys = {
                "fullscreen":   K_f,
                "quit"      :   K_ESCAPE,
                "badguy"    :   K_RETURN,
                "tower"     :   K_t,
                "upgrade"   :   K_a,
                "select"    :   K_SPACE,
                "sell_tw"   :   K_v,
                "construction" : K_c,
                "research" : K_r,
                "upgrades" : K_m,
                "special"  : K_s,
                "bouton1"  : K_F1,
                "bouton2"  : K_F2,
                "bouton3"  : K_F3,
                "bouton4"  : K_F4,
                "bouton5"  : K_F5,
                "bouton6"  : K_F6,
                "bouton7"  : K_F7,
                "bouton8"  : K_F8,
                "bouton9"  : K_F9,
                "bouton10"  : K_F10,
                "menu_down" : K_DOWN,
                "menu_up" : K_UP,
                "menu_select" : K_RETURN,
                }
    settings["keys"] = keys
    settings["touches_boutons"] = [keys[a] for a in keys if a[:6] == "bouton"]
    s["settings"] = settings
    s.close()

def manage_configuration(argv):
    
    config_file = "mptd.conf"
    if not os.path.exists(config_file):
        create_default_config(config_file)
    s = shelve.open(config_file)
    settings = s["settings"]
    s.close()
    
    if not TEST:
        mainmenu = menu.menu(settings["keys"])
        optionsmenu = menu.menu(settings["keys"])
        touchesmenu = menu.menu(settings["keys"])
        mainmenu.add_item(menu.item("Menu principal",None))
        mainmenu.add_item(menu.item("Lancer le jeu solo",("solo",None)))
        mainmenu.add_item(menu.item("Lancer le jeu multijoueur",("multi",None)))
        mainmenu.add_item(menu.item("Options",("menu",optionsmenu)))
        mainmenu.add_item(menu.item("Quitter",("quit",None)))
        
        optionsmenu.add_item(menu.item("Options",None))
        optionsmenu.add_item(menu.item("Activer le plein ecran",("toggle fullscreen",settings)))
        optionsmenu.add_item(menu.item("Changer l'IP du serveur",("input server_ip",settings)))
        optionsmenu.add_item(menu.item("Changer le port du serveur",("input server_port",settings)))
        optionsmenu.add_item(menu.item("Configurer les touches",("menu",touchesmenu)))
        optionsmenu.add_item(menu.item("Retour au menu",("quit",None)))
        
        touchesmenu.add_item(menu.item("Configuration des touches",None))
        liste_touches = [k for k in settings["keys"]]
        liste_touches.sort()
        for k in liste_touches:
            touchesmenu.add_item(menu.item(menu.key_name[k],("keyconf " + k, settings)))
        
        result = mainmenu.mainloop()
    else:
        result = ['solo',]
    quitter = False
    if result:
        if result[0] == "solo":
            settings["solo"] = True
        if result[0] == "multi":
            settings["solo"] = False
        if result[0] == "quit":
            quitter = True
    
    try:
        opts, args = getopt.getopt(argv, "f1nhs:p:", ["fullscreen","one-player","no-network","help","server","port"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-f", "--fullscreen"):
            settings["fullscreen"] = True
        if opt in ("-1", "--one-player"):
            settings["server"] = None
            settings["solo"] = True
        if opt in ("-n", "--no-network"):
            settings["server"] = None
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        if opt in ("-s", "--server"):
            settings["server"] = arg
        if opt in ("-p", "--port"):
            settings["port"] = int(arg)
            
    s = shelve.open(config_file)
    s["settings"] = settings
    s.close()
    if not quitter:
        return settings
    return None

def main(argv):
    print "Main using LiveWires package"

    settings = manage_configuration(argv)
    if settings:
        s = MptdScreen(settings)
        s.mainloop()

if __name__ == "__main__":
    main(sys.argv[1:])
