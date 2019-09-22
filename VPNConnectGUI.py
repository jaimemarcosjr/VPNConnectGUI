#!/usr/bin/python3
import gi, sys, os, threading, re, workaround as work, dialog, sys 
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from pref import preferences

whatis = lambda obj: print(type(obj), "\n\t" + "\n\t".join(dir(obj)))

pr = preferences()

pid = pr.checkPID()
if pid != "":
    if pr.checkIfRunning(int(pid)):
        is_process_name = False
        proc = work.executeCommandRealTime(["ps -o cmd= " + pid])
        while True:
            line = proc.readline().decode().strip()
            if line == "/usr/bin/python3 ./VPNConnectGUI.py":
                is_process_name = True
            if not line: break
        if(is_process_name):
            dialog.on_warn(None, "Existing Process", "Check your system tray!")
            sys.exit(0)
        else: work.executeCommand("rm -rf " + pr.pathOfPID())
    else: work.executeCommand("rm -rf " + pr.pathOfPID())

abuilder = Gtk.Builder()
abuilder.add_from_file("main.glade")

# Getting widgets
form = abuilder.get_object("mainForm")

btnConnect = abuilder.get_object("btnConnect")

tvList = abuilder.get_object("tvList")
lsList = abuilder.get_object("lsList")

dPref = abuilder.get_object("dPref")

siStatus = abuilder.get_object("siStatus")

adVPN = abuilder.get_object("adVPN")

tvLog = abuilder.get_object("tvLog")
lsLog = abuilder.get_object("lsLog")
swLog = abuilder.get_object("swLog")

ibStatus = abuilder.get_object("ibStatus")
iStatus = abuilder.get_object("iStatus")
lblStatus = abuilder.get_object("lblStatus")
sStatus = abuilder.get_object("sStatus")
# end #
test = [["test"], ["test1"], ["test2"]]


#selection changed in tvList
def onSelectionChanged(tree_selection):
    (model, pathlist) = tree_selection.get_selected_rows()
    for path in pathlist:
        tree_iter = model.get_iter(path)
        value = model.get_value(tree_iter, 0)
        work.currentSelected = value
        if (value.strip() != ""):
            print(work.currentSelected)

def onKeyReleased(widget, event):
    if event.keyval == Gdk.KEY_Return:
        btnConnect.clicked()


def getList():
    lsList.clear()
    cmd = ["ls " + pr.getDirectory()[0] + " | grep '.ovpn'"]
    resList = work.executeCommand(cmd)
    for list in resList:
        lsList.append(list.decode().split())


def connectRealtime(cmd):
    p = work.executeCommandRealTime(cmd)
    work.status = "idle"
    iStatus.set_from_stock(Gtk.STOCK_INFO, Gtk.IconSize.BUTTON)
    lblStatus.set_text("Connecting....")
    sStatus.start()
    siStatus.set_from_icon_name("network-vpn-acquiring")
    siStatus.set_tooltip_text("OpenVPN GUI: Connecting")
    while True:
        line = p.readline().decode().strip()
        lsLog.append([line])
        if "Request dismissed" in line or "Not authorized" in line:
            iStatus.set_from_stock(Gtk.STOCK_DISCONNECT, Gtk.IconSize.BUTTON)
            lblStatus.set_text("Your are now disconnected")
            work.status = "disconnected"
            sStatus.stop()
            work.executeCommand(
                "notify-send 'Warning' 'You are now disconnected!' --icon=security-low"
            )
            siStatus.set_from_icon_name("network-vpn")
            siStatus.set_tooltip_text("OpenVPN GUI: Disconnected")
        if "Initialization Sequence Completed" in line:
            iStatus.set_from_stock(Gtk.STOCK_CONNECT, Gtk.IconSize.BUTTON)
            lblStatus.set_text("Your are now connected")
            work.status = "connected"
            sStatus.stop()
            work.executeCommand(
                "notify-send 'Success' 'You are now connected!' --icon=security-high"
            )
            siStatus.set_from_icon_name("nm-vpn-standalone-lock")
            siStatus.set_tooltip_text("OpenVPN GUI: Connected")
        if "process exiting" in line:
            iStatus.set_from_stock(Gtk.STOCK_DISCONNECT, Gtk.IconSize.BUTTON)
            lblStatus.set_text("Your are now disconnected")
            work.executeCommand(
                "notify-send 'Warning' 'You are now disconnected!' --icon=security-low"
            )
            if "auth-failure" in line:
                iStatus.set_from_stock(Gtk.STOCK_DIALOG_ERROR,
                                       Gtk.IconSize.BUTTON)
                lblStatus.set_text("Invalid login credentials")
                work.executeCommand(
                    "notify-send 'Auth failure!' 'You may not allowed to access or username and password are incorrect' --icon=changes-prevent"
                )
            work.status = "disconnected"
            sStatus.stop()
            siStatus.set_from_icon_name("network-vpn")
            siStatus.set_tooltip_text("OpenVPN GUI: Disconnected")
        if "Cannot resolve host address" in line:
            iStatus.set_from_stock(Gtk.STOCK_INFO, Gtk.IconSize.BUTTON)
            lblStatus.set_text("Temporary failure in name resolution")
            work.status = "idle"
            sStatus.stop()
            work.executeCommand(
                "notify-send 'Warning' 'Please check you internet connection' --icon=network-wireless-offline-symbolic.symbolic"
            )
            siStatus.set_from_icon_name("network-vpn")
            siStatus.set_tooltip_text("OpenVPN GUI: Idle")
        if "Restart pause" in line:
            iStatus.set_from_stock(Gtk.STOCK_INFO, Gtk.IconSize.BUTTON)
            lblStatus.set_text("Reconnecting....")
            work.status = "idle"
            sStatus.start()
            work.executeCommand(
                "notify-send 'Info' 'Reconnecting....' --icon=dialog-information"
            )
            siStatus.set_from_icon_name("network-vpn-acquiring")
            siStatus.set_tooltip_text("OpenVPN GUI: Reconnecting")
        if not line: break


def disconnect():
    if work.status is "disconnected":
        return
    cmd = [
        "/usr/bin/pkexec --disable-internal-agent pkill openvpn && echo \"return\""
    ]
    res = work.executeCommandRealTime(cmd)
    work.executeCommand("rm -rf " + pr.tempFolder())
    return res

def closeForm(arg):
    if work.status is "connected" or work.status is "idle":
        if not dialog.on_question(
                form, "Warning", "Your are " + work.status +
                ". Are you sure you want to exit? You will be disonnected."
        ):
            return True
        else:
            p = disconnect()
            while True:
                line = p.readline().decode().strip()
                if "Request dismissed" in line or "Not authorized" in line:
                    return True
                if not line: break
    work.executeCommand("rm -rf " + pr.pathOfPID())
    pr.close()
    sys.exit(0)

def show_about_dialog(arg):
    adVPN.run()
    adVPN.hide()

class main:
    def onShow(self, *a, **kv):
        if pr.form_show_inc == 0:
            tree_selection = tvList.get_selection()
            tree_selection.connect("changed", onSelectionChanged)
            tvList.connect("key-release-event", onKeyReleased)
            getList()
            for i, column_title in enumerate(["VPN Files"]):
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(column_title, renderer, text=i)
                tvList.append_column(column)

            for i, column_title in enumerate(["Log"]):
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(column_title, renderer, text=i)
                tvLog.append_column(column)
        pr.form_show_inc += 1

    def on_mainForm_delete_event(self, a, *b):
        self.hide()
        return True

    def about_activate(self):
        show_about_dialog(1)

    def on_btnDisconnect_clicked(self, *a, **kv):
        disconnect()

    def on_btnConnect_clicked(self, *a, **kv):
        if work.currentSelected.strip() is "":
            return True
        if work.status is "connected" or work.status is "idle":
            dialog.on_warn(form, "", "Disconnect first!")
            return True
        proxy = pr.getProxy()
        cmdProxy = ""
        if not proxy[0].strip() or not proxy[1].strip():
            print("No proxy")
        else:
            if (proxy[2]):
                cmdProxy = " --http-proxy " + proxy[1] + " " + proxy[0]
        cred_path = pr.generateTempFileCred(pr.getCred()[0], pr.getCred()[1])
        cmd = [
            "/usr/bin/pkexec --disable-internal-agent openvpn --config " +
            pr.getDirectory()[0] + "/" + re.escape(work.currentSelected) +
            " --auth-user-pass " + cred_path + cmdProxy
        ]
        thread = threading.Thread(target=connectRealtime, args=(cmd, ))
        thread.daemon = True
        thread.start()

    def mPrefClick(self, *a, **kv):
        proxyRes = pr.getProxy()
        abuilder.get_object("eIP").set_text(proxyRes[1])
        abuilder.get_object("ePort").set_text(proxyRes[0])
        abuilder.get_object("cbE").set_active(
            str(proxyRes[2]).strip() is "True")

        credRes = pr.getCred()
        abuilder.get_object("eCredUser").set_text(credRes[0])
        abuilder.get_object("eCredPass").set_text(credRes[1])

        dirRes = pr.getDirectory()
        abuilder.get_object("fcDir").set_filename(dirRes[0])

        dPref.show()

    def on_dPref_delete_event(self, *a, **kv):
        self.hide()
        return True

    def btnSaveProxy_clicked_cb(self, *a, **kv):
        ip = abuilder.get_object("eIP").get_text()
        port = abuilder.get_object("ePort").get_text()
        e = abuilder.get_object("cbE").get_active()

        if not ip.strip() and not port.strip():
            print("Both empty are accepted")
        elif not ip.strip() or not port.strip():
            dialog.on_warn(dPref, "Fill all form or leave all empty. ",
                           "Cannot leave on empty")
            return
        pr.insertProxy(ip, port, e)
        dialog.on_info(dPref, "Success. ", "Proxy saved!")

    def btnDir_clicked_cb(self, *a, **kv):
        dir = abuilder.get_object("fcDir").get_filename()
        if not dir.strip():
            dialog.on_warn(dPref, "Fill all form. ", "All forms are required!")
            return
        pr.insertDir(dir)
        dialog.on_info(dPref, "Success. ", "Directory saved!")
        getList()

    def btnSaveCred_clicked_cb(self, *a, **kv):
        user = abuilder.get_object("eCredUser").get_text()
        pas = abuilder.get_object("eCredPass").get_text()
        if not pas.strip() or not user.strip():
            dialog.on_warn(dPref, "Fill all form. ", "All forms are required!")
            return
        pr.insertCred(user, pas)
        dialog.on_info(dPref, "Success. ", "VPN Credentials saved!")

    def on_seVPN_search_changed(self, *a, **kv):
        if not self.get_text().strip():
            getList()
            return
        cmd = [
            "ls " + pr.getDirectory()[0] + " | grep '.ovpn' | grep -i '" +
            self.get_text().strip() + "'"
        ]
        resList = work.executeCommand(cmd)
        lsList.clear()
        for list in resList:
            lsList.append(list.decode().split())

    def tvLog_size_allocate_cb(self, *a, **kv):
        upper = swLog.get_vadjustment().get_upper()
        page_size = swLog.get_vadjustment().get_page_size()
        adj = Gtk.Adjustment()

        adj.set_upper(upper - page_size)
        adj.set_value(upper - page_size)
        swLog.set_vadjustment(adj)
    def siStatus_activate_cb(self):   
        if form.get_visible():
            form.hide()
        else: 
            form.show()
    def siStatus_popup_menu_cb(self, button, activate_time):        
        mStatusmenu = Gtk.Menu()

        about = Gtk.MenuItem()
        about.set_label("About")
        about.connect("activate", show_about_dialog)
        mStatusmenu.append(about)

        quit = Gtk.MenuItem()
        quit.set_label("Quit")
        quit.connect("activate", closeForm)
        mStatusmenu.append(quit)

        mStatusmenu.show_all()

        mStatusmenu.popup(None, None, None, self, button, activate_time)

abuilder.connect_signals(main)
param = sys.argv
for index, item in enumerate(param):
    if item == "--show":
        form.show()
siStatus.set_visible(True)
siStatus.set_tooltip_text("OpenVPN GUI: Disconnected")
pr.createPID()
Gtk.main()