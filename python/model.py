delta_t = 1

class event:
    time = 0
    test = 0
    R = 0
    r = 0
    S = 0
    s = 0
    I = 0
    i = 0
    Q = 0
    q = 0
    E = 0
    e = 0
    def __init__ (self, time):
        self.time = time

    def update_test_euler (self, parameters_store, event, string_to_use):
        import math
        dtest_dt = 2*math.sin(event.time)
        self.test = event.test + dtest_dt*(self.time-event.time)

    def update_s_euler (self, parameters_store, event, string_to_use):
        ds_dt = -parameters_store[string_to_use]["beta"]*parameters_store[string_to_use]["k"]*event.s*event.i+parameters_store[string_to_use]["gamma"]*(1-event.e-event.s-event.i-event.q)
        self.s = event.s + ds_dt*(self.time-event.time)
        self.S = self.s * parameters_store[string_to_use]["N"]
        
    def update_e_euler (self, parameters_store, event, event_past, string_to_use):
        de_dt = parameters_store[string_to_use]["beta"]*parameters_store[string_to_use]["k"]*event.s*event.i-parameters_store[string_to_use]["beta"]*parameters_store[string_to_use]["k"]*event_past.s*event_past.i
        self.e = event.e + de_dt*(self.time-event.time)
        self.E = self.e * parameters_store[string_to_use]["N"]

    def update_i_euler (self, parameters_store, event, event_past, string_to_use):
        di_dt = parameters_store[string_to_use]["beta"]*parameters_store[string_to_use]["k"]*event_past.s*event_past.i-parameters_store[string_to_use]["d1"]*event.i-parameters_store[string_to_use]["delta"]*event.i
        self.i = event.i + di_dt*(self.time-event.time)
        self.I = self.i * parameters_store[string_to_use]["N"]
        # print ("t " +str(self.time)+" i "+str(self.i)+" I "+str(self.I)+" di/dt "+str( di_dt))
        # print (" di/dt = "+str(parameters_store[string_to_use]["beta"]*parameters_store[string_to_use]["k"]*event_past.s*event_past.i)+"-"+str(parameters_store[string_to_use]["d1"]*event.i+parameters_store[string_to_use]["delta"]*event.i))
    def update_q_euler (self, parameters_store, event, string_to_use):
        dq_dt = parameters_store[string_to_use]["delta"]*event.i-parameters_store[string_to_use]["d2"]*event.i-parameters_store[string_to_use]["mu"]*event.q
        self.q = event.q + dq_dt*(self.time-event.time)
        self.Q = self.q * parameters_store[string_to_use]["N"]
        
    def update_r_euler (self, parameters_store, event, string_to_use):
        dr_dt = parameters_store[string_to_use]["mu"]*event.q-parameters_store[string_to_use]["gamma"]*event.r
        self.r = event.r + dr_dt * (self.time-event.time)
        self.R = self.r * parameters_store[string_to_use]["N"]

    def update_midpoint (self, parameters_store, event_precedent, event_past, string_to_use):
        event_half_point = event (event_precedent.time+delta_t/2)
        event_half_point.update_s_euler (parameters_store, event_precedent, string_to_use)
        event_half_point.update_e_euler (parameters_store, event_precedent, event_past, string_to_use)
        event_half_point.update_i_euler (parameters_store, event_precedent, event_past, string_to_use)
        event_half_point.update_q_euler (parameters_store, event_precedent, string_to_use)
        event_half_point.update_r_euler (parameters_store, event_precedent, string_to_use)
        event_half_point.update_test_euler (parameters_store, event_precedent, string_to_use)

        de_dt = parameters_store[string_to_use]["beta"]*parameters_store[string_to_use]["k"]*event_half_point.s*event_half_point.i-parameters_store[string_to_use]["beta"]*parameters_store[string_to_use]["k"]*event_past.s*event_past.i
        self.e = event_precedent.e + de_dt*(self.time-event_precedent.time)
        self.E = self.e * parameters_store[string_to_use]["N"]

        di_dt = parameters_store[string_to_use]["beta"]*parameters_store[string_to_use]["k"]*event_past.s*event_past.i-parameters_store[string_to_use]["d1"]*event_half_point.i-parameters_store[string_to_use]["delta"]*event_half_point.i
        self.i = event_precedent.i + di_dt*(self.time-event_precedent.time)
        self.I = self.i * parameters_store[string_to_use]["N"]
        
        dq_dt = parameters_store[string_to_use]["delta"]*event_half_point.i-parameters_store[string_to_use]["d2"]*event_half_point.i-parameters_store[string_to_use]["mu"]*event_half_point.q
        self.q = event_precedent.q + dq_dt*(self.time-event_precedent.time)
        self.Q = self.q * parameters_store[string_to_use]["N"]

        dr_dt = parameters_store[string_to_use]["mu"]*event_half_point.q-parameters_store[string_to_use]["gamma"]*event_half_point.r
        self.r = event_precedent.r + dr_dt*(self.time-event_precedent.time)
        self.R = self.r * parameters_store[string_to_use]["N"]

        ds_dt = -parameters_store[string_to_use]["beta"]*parameters_store[string_to_use]["k"]*event_half_point.s*event_half_point.i+parameters_store[string_to_use]["gamma"]*(1-event_half_point.e-event_half_point.s-event_half_point.i-event_half_point.q)
        self.s = event_precedent.s + ds_dt*(self.time-event_precedent.time)
        self.S = self.s * parameters_store[string_to_use]["N"]

        import math
        dtest_dt = 2*math.sin(event_half_point.time)
        self.test = event_precedent.test + dtest_dt*(self.time-event_precedent.time)

        
        if parameters_store["simulation_parameters"]["VERBOSE"] == "TRUE":
            
            print( " > t "+str(self.time-delta_t)+" s "+str(event_precedent.s)+" e "+str(event_precedent.e)+" i "+str(event_precedent.i)+" q "+str(event_precedent.q)+" r "+str(event_precedent.r))
            print( " > half-point t "+str(event_half_point.time)+" s "+str(event_half_point.s)+" e "+str(event_half_point.e)+" i "+str(event_half_point.i)+" q "+str(event_half_point.q)+" r "+str(event_half_point.r))
            print( " > derivative dsdt "+str(ds_dt)+" dedt "+str(de_dt)+" didt "+str(di_dt)+" dqdt "+str(dq_dt)+" drdt "+str(dr_dt))
            print( " > t "+str(self.time)+" s "+str(self.s)+" e "+str(self.e)+" i "+str(self.i)+" q "+str(self.q)+" r "+str(self.r))
 