# Basic Python Plugin Example
#
# Author: GizMoCuz
#
"""
<plugin key="AndinoX1Plug" name="Andino X1" author="Hans Eichbaum" version="1.0.0" externallink="https://andino.shop">
    <description>
        <h2>Andino X1</h2><br/>
        <ul style="list-style-type:square">
            <li>Reading out Input 1 and Input 2</li>
            <li>Controlling Relay 1 and Relay 2</li>
        </ul>
    </description>
    <params>
        <param field="SerialPort" label="Serial Port" width="200px" required="true" default="/dev/ttyAMA0" />
    </params>
</plugin>
"""
import Domoticz

andinoSerialConn=None


class BasePlugin:
    enabled = False
    fresh_start = True
    prev_states = []

    prev_state_input1=None

    def __init__(self):
        #self.var = 123
        return

    def onStart(self):
        global andinoSerialConn
        Domoticz.Log("onStart called")

        andinoSerialConn = Domoticz.Connection(Name="Serial Connection", Transport="Serial", Protocol="Line", Address=Parameters["SerialPort"], Baud=38400)
        andinoSerialConn.Connect()


        if (len(Devices)==0):
            Domoticz.Device(Name="Input 1", Unit=1, TypeName="Switch").Create()
            Domoticz.Device(Name="Input 2", Unit=2, TypeName="Switch").Create()

            Domoticz.Device(Name="Relay 1", Unit=11, TypeName="Switch").Create()
            Domoticz.Device(Name="Relay 2", Unit=12, TypeName="Switch").Create()

            Domoticz.Device(Name="Relay 1 Pulse", Unit=21, TypeName="Switch").Create()
            Domoticz.Device(Name="Relay 2 Pulse", Unit=22, TypeName="Switch").Create()
            #todo read configuration of X1
            # now assuming HARD=0
            Domoticz.Log("Devices created.")

        return


    def onStop(self):
        Domoticz.Log("onStop called")


    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")
        if (Status==0):
            Domoticz.Log("Connected successfully to: "+Parameters["SerialPort"])
            Connection.Send("SEND 5000\n")

        else:
            Domoticz.Log("Failed to connect ("+str(Status)+") to "+Parameters["SerialPort"])
        return True

    def onMessage(self, Connection, Data):

        strData = Data.decode("utf-8", "ignore")

        if (strData[0]==":"):
            states=strData[strData.rfind("{")+1:-1].split(',')

            if (self.fresh_start==True):
                #this is the first round, do nothing
                self.fresh_start=False
            else:
                for i in range(len(states)):
                    if (states[i]!=self.prev_states[i]):
                        nValue=0
                        sValue="Off"
                        if states[i]=="1":
                            nValue=1
                            sValue="On"

                        Domoticz.Log("New state Device ("+Devices[i+1].Name+'): '+sValue)
                        Devices[i+1].Update(nValue,sValue)

            self.prev_states=states.copy()

        for Device in Devices:
            #still alive
            Devices[Device].Touch()

        return

    def onCommand(self, Unit, Command, Level, Hue):
        global andinoSerialConn
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

        rel_state="0"
        if str(Command)=='On':
            rel_state="1"

        if (Unit>=10):
            rel_nr=int(Unit) % 10

            relCommand="RPU%s 2" % rel_nr
            if (int(Unit / 10)==1):
                relCommand="REL%s %s" % (rel_nr, rel_state)
                Devices[Unit].Update(int(rel_state),str(Command))

            Domoticz.Log("Sending Command: "+relCommand)
            andinoSerialConn.Send(relCommand+"\n" )
        else:
            Domoticz.Log("Nothing to do!")
        return


    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")
        for Device in Devices:
            Devices[Device].Update(nValue=Devices[Device].nValue, sValue=Devices[Device].sValue, TimedOut=1)
            Domoticz.Log("Connection '"+Connection.Name+"' disconnected.")
        return

    def onHeartbeat(self):
        #Domoticz.Log("onHeartbeat called")
        return


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
