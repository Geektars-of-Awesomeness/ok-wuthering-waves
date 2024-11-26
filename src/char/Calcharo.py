from src.char.BaseChar import BaseChar


class Calcharo(BaseChar):
    def do_perform(self):
        if self.has_intro:
            self.logger.debug('Calcharo wait intro animation')
            self.sleep(1)
            self.task.wait_in_team_and_world(time_out=3, raise_if_not_found=False)
            self.check_combat()
        #super().do_perform()

        self.click_echo()

        if self.liberation_available():    
            self.click_liberation()
            self.continues_normal_attack(3)
            self.heavy_attack()
            self.continues_normal_attack(3)

        if self.resonance_available():
            self.send_resonance_key()
            self.send_resonance_key()
            self.send_resonance_key()
            
        if self.is_forte_full():  
            self.heavy_attack(0.8)
        
        self.switch_next_char()           
