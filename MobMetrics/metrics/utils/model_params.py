from math import pi
def boundless_params(data):
    time_step = data.get('time_step')
    accel_max = data.get('accel_max')
    alpha = data.get('alpha')
    if not alpha:
        alpha = str(pi/2)

    return ["-t",time_step,"-m",accel_max,"-s",alpha]

def column_params(data):
    num_groups = data.get('num_groups')
    ref_pt_separation = data.get('ref_pt_separation')
    max_distance_group_center = data.get('max_distance_group_center')

    return ["-a",num_groups,"-r",ref_pt_separation,"-s",max_distance_group_center]

def nomadic_params(data):
    avg_nodes_group = data.get('avg_nodes_group') 
    max_distance_group_center = data.get('max_distance_group_center_n')
    group_size_stdd = data.get('group_size_stdd')
    ref_point_max_pause = data.get('ref_point_max_pause')

    return ["-a",avg_nodes_group,"-r",max_distance_group_center,"-s",group_size_stdd,"-c",ref_point_max_pause]

def probrandomwalk_params(data):
    time_interval_to_advance = data.get('time_interval_to_advance')

    return ["-t",time_interval_to_advance]

def pursue_params(data):
    max_speed = data.get('max_speed')
    min_speed = data.get('min_speed')
    aggressiveness = data.get('aggressiveness')
    pursue_randomness_magnitude = data.get('pursue_randomness_magnitude')

    return ["-o",max_speed,"-p",min_speed,"-k",aggressiveness,"-m",pursue_randomness_magnitude]

def randomdirection_params(data):
    min_pause_time = data.get('min_pause_time')

    return ["-o",min_pause_time]

def randomwaypoint_params(data):
    dimension = data.get("dimension")
    return ["-o", dimension] if dimension else []

def static_params(data):
    number_density_levels = data.get('number_density_levels')

    return ["-l",number_density_levels]

def disasterarea_params(data):
    return data.get('parameters').split(' ')

def chainscenario_params(data):
    return data.get('parameters').split(' ')

def originalgaussmarkov_params(data):
    return data.get('parameters').split(' ')

def gaussmarkov_params(data):
    return data.get('parameters').split(' ')

def manhattangrid_params(data):
    return data.get('parameters').split(' ')

def randomstreet_params(data):
    return data.get('parameters').split(' ')

def mslaw_params(data):
    return data.get('parameters').split(' ')

def randomwalk_params(data):
    return data.get('parameters').split(' ')

def rpgm_params(data):
    return data.get('parameters').split(' ')

def slaw_params(data):
    return data.get('parameters').split(' ')

def smooth_params(data):
    return data.get('parameters').split(' ')

def staticdrift_params(data):
    return data.get('parameters').split(' ')

def steadystaterandomwaypoint_params(data):
    return data.get('parameters').split(' ')

def swim_params(data):
    return data.get('parameters').split(' ')

def timm_params(data):
    return data.get('parameters').split(' ')

def tlw_params(data):
    return data.get('parameters').split(' ')


functions = {
    "Boundless": boundless_params,
    "ChainScenario": chainscenario_params,
    "Column": column_params,
    "DisasterArea": disasterarea_params,
    "OriginalGaussMarkov": originalgaussmarkov_params,
    "GaussMarkov": gaussmarkov_params,
    "ManhattanGrid": manhattangrid_params,
    "RandomStreet": randomstreet_params,
    "MSLAW": mslaw_params,
    "Nomadic": nomadic_params,
    "ProbRandomWalk": probrandomwalk_params,
    "Pursue": pursue_params,
    "RandomDirection": randomdirection_params,
    "RandomWalk": randomwalk_params,
    "RandomWaypoint": randomwaypoint_params,
    "RPGM": rpgm_params,
    "SLAW": slaw_params,
    "SMOOTH": smooth_params,
    "Static": static_params,
    "StaticDrift": staticdrift_params,
    "SteadyStateRandomWaypoint": steadystaterandomwaypoint_params,
    "SWIM": swim_params,
    "TIMM": timm_params,
    "TLW": tlw_params,
}
