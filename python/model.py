delta_t = 1
tampons_correction = [ 0.922225,1.398726,1.127037,0.937044,0.842808,0.954143,1.512722,0.959463,0.979616,1.038010,1.145676,0.473190,0.727764,1.146947,1.067260,0.865943,0.809771,1.010580,0.783723,0.602979,0.899449,0.871758,1.162601,1.215422,1.115899,0.728480,0.886271,1.097154,1.418849,1.244580,1.302248,1.004629,0.695862,1.017925,1.162711,1.320344,1.260629,1.202493,1.087064 ]
#tampons_correction = [0.9872441740531028, 1.5171133320108583, 1.200677130514623, 0.9520421565738633, 0.7960764843992927, 0.8210975843013235, 1.1688082397325879, 0.6592759007507154, 0.9231203025048135, 1.1625028227425118, 1.4169521485219272, 0.6187151142305568, 0.9782065727382999, 1.555073813272046, 1.4405145501154475, 1.1526374755485862, 1.0557577174831618, 1.2841144636079982, 0.9670013115211192, 0.7204625618730867, 1.0386010857080965, 0.9713526028540029, 1.2486424227988266, 1.2572080115665005, 1.111021152481559, 0.6978343960679942, 0.8166094370647083, 0.9721837493206806, 1.2089306521422052, 1.0196431327189224, 1.0258230000706914, 0.7609268948346639]
min_t = 15
max_t = 25



def correct_delta_with_tampons (event_current, parameters_store,string_to_use, firstEvent=False):
    delta = parameters_store[string_to_use]["delta"]
    t0 = parameters_store["initial_conditions"]["t0"]

    # if 'postfit' in string_to_use and firstEvent:
    #     for n,t in enumerate(list(tampons_correction)):
    #         var = 0.20
    #         if n < 10:
    #             tampons_correction [n] = (1-1.2*0.2)*t 
    #         elif n < 20:
    #             tampons_correction [n] = (1+1.2*0.2)*t 
    #         elif n < 30:
    #             tampons_correction [n] = (1+0.8*0.2)*t 
    #         else:
    #             tampons_correction [n] = (1+0.0*0.2)*t 

    
    if parameters_store["simulation_parameters"]["IMPROVED_MODEL"] == "FALSE": return delta    
    if (event_current.time-t0) >= len (tampons_correction) : return delta 
    elif (event_current.time-t0) < 0: return delta
    else:
        return delta*tampons_correction[int (event_current.time-t0)]
    # delta_max = parameters_store[string_to_use]["delta"]
    # return delta_max
    # t0 = parameters_store["initial_conditions"]["t0"]
    # if parameters_store["simulation_parameters"]["IMPROVED_MODEL"] == "FALSE": return delta_max
    # delta_min = 0.1*delta_max
    # if (event_current.time-t0) < min_t: return delta_min
    # elif (event_current.time-t0) < max_t: return delta_min + abs(delta_max-delta_min)/abs(max_t-min_t)* (event_current.time-min_t)
    # else: return delta_max

def schedule_k (event_current, parameters_store,string_to_use):
    reopening_t = 66
    duration_reopeining = 180
    t0 = parameters_store["initial_conditions"]["t0"]
    k_max = parameters_store[string_to_use]["k"]
    if parameters_store["simulation_parameters"]["IMPROVED_MODEL"] == "FALSE": return k_max
    k_min = min (2,int (k_max/3))
    if (event_current.time-t0) <= min_t: return k_max
    elif (event_current.time-t0) < max_t: return k_max - abs(k_min-k_max)/abs(max_t-min_t)* (event_current.time-t0-min_t)
    else:
        if parameters_store["simulation_parameters"]["IMPROVED_MODEL"] == "REOPENING" and (event_current.time-t0) > reopening_t :
            if (event_current.time-t0) < reopening_t+duration_reopeining:
                return k_min +(k_max-k_min)/abs(duration_reopeining)* (event_current.time-t0-reopening_t)
            else:
                return k_max
        #    return k_max
        else:
            return k_min
        
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
    D = 0
    d = 0
    delta = 0
    k = 0
    TOT = 0
    tot = 0
    def __init__ (self, time, parameters_store, string_to_use):
        self.time = time
        self.delta = correct_delta_with_tampons (self, parameters_store, string_to_use, (time==0) )
        self.k = schedule_k (self, parameters_store, string_to_use)
       
    def update_test_euler (self, parameters_store, event, string_to_use):
        import math
        dtest_dt = 2*math.sin(event.time)
        self.test = event.test + dtest_dt*(self.time-event.time)

    def update_s_euler (self, parameters_store, event, string_to_use):
        ds_dt = -parameters_store[string_to_use]["beta"]*self.k*event.s*event.i+parameters_store[string_to_use]["gamma"]*(event.r)
        self.s = event.s + ds_dt*(self.time-event.time)
        self.S = self.s * parameters_store[string_to_use]["N"]
        
    def update_e_euler (self, parameters_store, event, event_past, string_to_use):
        de_dt = parameters_store[string_to_use]["beta"]*self.k*event.s*event.i-parameters_store[string_to_use]["beta"]*self.k*event_past.s*event_past.i
        self.e = event.e + de_dt*abs(self.time-event.time)
        self.E = self.e * parameters_store[string_to_use]["N"]

    def update_i_euler (self, parameters_store, event, event_past, string_to_use):
        di_dt = parameters_store[string_to_use]["beta"]*self.k*event_past.s*event_past.i-parameters_store[string_to_use]["d1"]*event.i-self.delta*event.i
        self.i = event.i + di_dt*abs(self.time-event.time)
        self.I = self.i * parameters_store[string_to_use]["N"]
        # print ("t " +str(self.time)+" i "+str(self.i)+" I "+str(self.I)+" di/dt "+str( di_dt))
        # print (" di/dt = "+str(parameters_store[string_to_use]["beta"]*self.k*event_past.s*event_past.i)+"-"+str(parameters_store[string_to_use]["d1"]*event.i+self.delta*event.i))
    def update_q_euler (self, parameters_store, event, string_to_use):
        dq_dt = self.delta*event.i-parameters_store[string_to_use]["d2"]*event.i-parameters_store[string_to_use]["mu"]*event.q
        self.q = event.q + dq_dt*abs(self.time-event.time)
        self.Q = self.q * parameters_store[string_to_use]["N"]
        
    def update_r_euler (self, parameters_store, event, string_to_use):
        dr_dt = parameters_store[string_to_use]["mu"]*event.q-parameters_store[string_to_use]["gamma"]*event.r
        self.r = event.r + dr_dt * abs(self.time-event.time)
        self.R = self.r * parameters_store[string_to_use]["N"]

    def update_midpoint (self, parameters_store, event_precedent, event_past, string_to_use):
        event_half_point = event (event_precedent.time+delta_t/2, parameters_store, string_to_use)
        event_half_point.update_s_euler (parameters_store, event_precedent, string_to_use)
        event_half_point.update_e_euler (parameters_store, event_precedent, event_past, string_to_use)
        event_half_point.update_i_euler (parameters_store, event_precedent, event_past, string_to_use)
        event_half_point.update_q_euler (parameters_store, event_precedent, string_to_use)
        event_half_point.update_r_euler (parameters_store, event_precedent, string_to_use)
        event_half_point.update_test_euler (parameters_store, event_precedent, string_to_use)

        de_dt = parameters_store[string_to_use]["beta"]*self.k*event_half_point.s*event_half_point.i-parameters_store[string_to_use]["beta"]*event_past.k*event_past.s*event_past.i
        self.e = event_precedent.e + de_dt*abs(self.time-event_precedent.time)
        self.E = self.e * parameters_store[string_to_use]["N"]

        di_dt = parameters_store[string_to_use]["beta"]*event_past.k*event_past.s*event_past.i-parameters_store[string_to_use]["d1"]*event_half_point.i-self.delta*event_half_point.i
        self.i = event_precedent.i + di_dt*abs(self.time-event_precedent.time)
        self.I = self.i * parameters_store[string_to_use]["N"]
        
        dq_dt = self.delta*event_half_point.i-parameters_store[string_to_use]["d2"]*event_half_point.i-parameters_store[string_to_use]["mu"]*event_half_point.q
        self.q = event_precedent.q + dq_dt*abs(self.time-event_precedent.time)
        self.Q = self.q * parameters_store[string_to_use]["N"]

        dr_dt = parameters_store[string_to_use]["mu"]*event_half_point.q-parameters_store[string_to_use]["gamma"]*event_half_point.r
        self.r = event_precedent.r + dr_dt*abs(self.time-event_precedent.time)
        self.R = self.r * parameters_store[string_to_use]["N"]

        ds_dt = -parameters_store[string_to_use]["beta"]*self.k*event_half_point.s*event_half_point.i+parameters_store[string_to_use]["gamma"]*(event_half_point.r)
        self.s = event_precedent.s + ds_dt*abs(self.time-event_precedent.time)
        self.S = self.s * parameters_store[string_to_use]["N"]

        self.d = 1 - self.s - self.e - self.i - self.q - self.r
        self.D = self.d * parameters_store[string_to_use]["N"]

        self.tot = self.q + self.r + self.d
        self.TOT = self.tot * parameters_store[string_to_use]["N"]
        
        import math
        dtest_dt = 2*math.sin(event_half_point.time)
        self.test = event_precedent.test + dtest_dt*abs(self.time-event_precedent.time)

        
        if parameters_store["simulation_parameters"]["VERBOSE"] == "TRUE":
            
            print( " > t "+str(self.time-delta_t)+" s "+str(event_precedent.s)+" e "+str(event_precedent.e)+" i "+str(event_precedent.i)+" q "+str(event_precedent.q)+" r "+str(event_precedent.r)+" d "+str(event_precedent.d))
            print( " > schedule k "+str(self.k)+" delta "+str(self.delta))
            print( " > half-point t "+str(event_half_point.time)+" s "+str(event_half_point.s)+" e "+str(event_half_point.e)+" i "+str(event_half_point.i)+" q "+str(event_half_point.q)+" r "+str(event_half_point.r))
            print( " > derivative dsdt "+str(ds_dt)+" dedt "+str(de_dt)+" didt "+str(di_dt)+" dqdt "+str(dq_dt)+" drdt "+str(dr_dt))
            print( " > t "+str(self.time)+" s "+str(self.s)+" e "+str(self.e)+" i "+str(self.i)+" q "+str(self.q)+" r "+str(self.r)+" d "+str( self.d))
            print( " > t "+str(self.time)+" s "+str(self.S)+" e "+str(self.E)+" i "+str(self.I)+" q "+str(self.Q)+" r "+str(self.R)+" d "+str( self.D))
            print( " > n "+str(self.time)+" total "+str(self.S+self.e+self.i+self.q+self.r+self.d))
 
            
