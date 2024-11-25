from qfluentwidgets import FluentIcon

from ok.Task import CannotFindException, WaitFailedException
from ok.logging.Logger import get_logger
from src.task.BaseCombatTask import BaseCombatTask, CharDeadException

logger = get_logger(__name__)

boss_config = {
    'Mech Abomination': {"walk_sec" : 10, "use_custom_teleport" : False},
    'Inferno Rider': {"walk_sec" : 5, "use_custom_teleport" : False},
    'Fallacy of No Return': {"walk_sec" : 10, "use_custom_teleport" : False},
    'Bell-Borne Geochelone': {"walk_sec" : 6, "use_custom_teleport" : False}, 
    'Crownless': {"walk_sec" : 7, "use_custom_teleport" : False}, 
    'Thundering Mephis': {"walk_sec" : 5, "use_custom_teleport" : False}, 
    'Tempest Mephis': {"walk_sec" : 4, "use_custom_teleport" : False},    
    'Feilian Beringal': {"walk_sec" : 10, "use_custom_teleport" : False},
    'Mourning Aix': {"walk_sec" : 6, "use_custom_teleport" : False}, 
    'Impermanence Heron': {"walk_sec" : 6, "use_custom_teleport" : False},
    'Lampylumen Myriad': {"walk_sec" : 5, "use_custom_teleport" : False}, 
}

class FarmWorldBossTask(BaseCombatTask):

    def __init__(self):
        super().__init__()
        self.description = "Drop a waypoint on the following bosses, then click Start:\nInferno Rider, Mech Abomination"
        self.name = "Farm World Boss"
        self.boss_names = list(boss_config.keys())
        self.boss_names.insert(0, "N/A")

        self.find_echo_method = ['Walk', 'Run in Circle', 'Turn Around and Search']

        default_config = {
            'Farm All World Bosses': True,
            'All Echo Pickup Method': 'Turn Around and Search',
            'Boss1': 'N/A',
            'Boss1 Echo Pickup Method': 'Turn Around and Search',
            'Boss2': 'N/A',
            'Boss2 Echo Pickup Method': 'Turn Around and Search',
            'Boss3': 'N/A',
            'Boss3 Echo Pickup Method': 'Turn Around and Search',
            'Repeat Farm Count': 1000
        }
        self.config_type['All Echo Pickup Method'] = {'type': "drop_down", 'options': self.find_echo_method}
        self.config_type['Boss1 Echo Pickup Method'] = {'type': "drop_down", 'options': self.find_echo_method}
        self.config_type['Boss2 Echo Pickup Method'] = {'type': "drop_down", 'options': self.find_echo_method}
        self.config_type['Boss3 Echo Pickup Method'] = {'type': "drop_down", 'options': self.find_echo_method}
        default_config.update(self.default_config)
        self.default_config = default_config
        self.config_type["Boss1"] = {'type': "drop_down", 'options': self.boss_names}
        self.config_type["Boss2"] = {'type': "drop_down", 'options': self.boss_names}
        self.config_type["Boss3"] = {'type': "drop_down", 'options': self.boss_names}
        self.config_description = {
            'Level': '(1-6) Important, Choose which level to farm, lower levels might not produce a echo',
            'Entrance Direction': 'Choose Forward for Dreamless, Backward for Jue'
        }
        self.config_type["Entrance Direction"] = {'type': "drop_down", 'options': ['Forward', 'Backward']}
        self.crownless_pos = (0.9, 0.4)
        self.icon = FluentIcon.GLOBE

    # not current in use because not stable, right now using one click to scroll down

    def run(self):
        self.set_check_monthly_card()
        self.check_main()
        count = 0
        farm_all = self.config.get('Farm All World Bosses')
        method = self.config.get('All Echo Pickup Method', 'Walk')

        boss_list = []
        if farm_all:
            boss_list = self.boss_names
        else:
            for i in range(1, 4):
                key = 'Boss' + str(i)
                boss_list.append(self.config.get(key))
        
        while True:
            for boss_name in boss_list:
                if boss_name != 'N/A':
                    count += 1
                        
                    use_custom_teleport = boss_config[boss_name]['use_custom_teleport']

                    try:
                        self.teleport_to_boss(boss_name, use_custom=use_custom_teleport)
                        walk_sec = boss_config[boss_name]['walk_sec']                        
                        if not use_custom_teleport:
                            logger.info(f'walk to the boss for {walk_sec} sec')
                            self.walk_until_f(raise_if_not_found=False, time_out=walk_sec)

                        logger.info(f'farm echo combat once start')
                        if boss_name == 'Crownless':
                            self.wait_in_team_and_world(time_out=20)
                            self.sleep(2)
                            logger.info('Crownless walk to interact')
                            self.walk_until_f(raise_if_not_found=True, time_out=10, backward_time=1)
                            
                            in_combat = self.wait_until(self.in_combat, raise_if_not_found=False, time_out=10,
                                                        wait_until_before_delay=0)
                            if not in_combat:  # try click again
                                self.walk_until_f(raise_if_not_found=True, time_out=4)

                        elif boss_name == 'Bell-Borne Geochelone':
                            logger.info(f'sleep for the Bell-Borne model to appear')
                            self.sleep(15)

                        try:
                            self.combat_once(wait_before=0, wait_combat_time=30)
                        except CharDeadException:
                            logger.info(f'char dead try teleport to heal')
                            self.teleport_to_heal()
                            continue                    

                        logger.info(f'farm echo combat end')
                        if boss_name == 'Bell-Borne Geochelone':
                            logger.info(f'sleep for the Boss model to disappear')
                            self.sleep(5)
                        logger.info(f'farm echo move forward walk_until_f to find echo')

                        if not farm_all:
                            method = self.config.get(f'Boss{i} Echo Pickup Method', 'Walk')

                        if method == 'Run in Circle':
                            dropped = self.run_in_circle_to_find_echo()
                        elif method == 'Turn Around and Search':
                            dropped = self.turn_and_find_echo()
                        else:
                            dropped = self.walk_find_echo()
                        self.incr_drop(dropped)
                    except WaitFailedException:
                        logger.info(f'{boss_name}: WaitFailedException occured, moving to the next boss')
                        self.record_error_log(f'{boss_name}: WaitFailedException occured, moving to the next boss')
                        self.incr_skip_count(boss_name)
                        continue
                    except CannotFindException:
                        logger.info(f'{boss_name}: cannot find interact key, moving to the next boss')
                        self.record_error_log(f'{boss_name}: cannot find interact key, moving to the next boss')
                        self.incr_skip_count(boss_name)   
                        continue                                     

            if count <= 1:
                self.log_error('Must choose at least 2 Boss to Farm', notify=True)
                return
