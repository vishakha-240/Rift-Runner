import pygame
import random
import math
import os
import json

pygame.init()


width=900
height=600

screen=pygame.display.set_mode((width,height))
pygame.display.set_caption("Rift Runner")

background=(25,2,8)

void_edge=30
void_color=(10,0,4)
ember=(240,90,50)

player_x=220
player_y=height//2

player_width=50
player_height=40

player_velocity_y=0
gravity=0.5

thrust=-8
FPS=60
max_fall=11
clock=pygame.time.Clock()
cloak_angle=0
rune_angle=0
n=6

ledger_file=os.path.join(os.path.dirname(os.path.abspath(__file__)),"riftt_runner_ledger.json")

rift_width = 90
rift_gap_height = 190
rift_speed=4
rift_spacing=380 

base_speed=4.0
max_speed=8.0
speed_per_point=0.12

base_gap=200
min_gap=135
gap_shrink_per_point=2.5

max_gap_shift=160

stone_chance=0.30
slow_seconds=4.0
slow_factor=0.45

rifts=[]
shards=[]
particles=[]
stones=[]

def load_high_score():
   try:
      with open(ledger_file,"r",encoding="utf-8")as file:
         data=json.load(file)
         return int(data.get("high_score",0))
   except(OSError,ValueError,TypeError,AttributeError):
      return 0

game_state="ready"
running=True
score=0
dead_time=0
high_score=load_high_score()
new_record=False
slow_timer=0
time_factor=1.0




last_gap_y=(height-base_gap)//2
      
font_title=pygame.font.SysFont("georgia",72,bold=True)
font_big=pygame.font.SysFont("georgia",44,bold=True)
font_mid=pygame.font.SysFont("georgia",28)
font_small=pygame.font.SysFont("georgia",20)

cloak_image=pygame.image.load("cloakk.png").convert_alpha()
cloak_image=pygame.transform.scale(cloak_image,(70,80))


def current_gap(score):
   return int(max(min_gap,base_gap-score*gap_shrink_per_point))

def current_speed(score):
   return min(max_speed,base_speed+score*speed_per_point)




def create_shard(first=False):
   size=random.randint(30,110)
   if first:
      x=random.randint(0,width)
   else:
      x=width+size
   
   y=random.randint(0,height)
   speed=random.uniform(0.3,1.2)
   color=random.choice([(70,8,14),(45,5,10),(30,30,36),(95,14,22)])

   s=size//2

   points=[(random.randint(-s,s),random.randint(-s,s)) for _ in range(3)]
   
   return {
      "x":x,
      "y":y,
      "size":size,
      "speed":speed,
      "color":color,
      "points":points
   }



   
def save_high_score(value):
   try:
      with open(ledger_file,"w",encoding="utf-8") as file:
         json.dump({"high_score":value},file)
   except OSError:
      pass


def check_high_score():
   global high_score,new_record

   if score>high_score:
      high_score=score
      new_record=True
      save_high_score(high_score)





def draw_rune_circle(surface,cx,cy,radius,angle):
   layer=pygame.Surface((radius*2+6,radius*2+6),pygame.SRCALPHA)
   c=radius+3
   col=(255,120,60,60)
   pygame.draw.circle(layer,col,(c,c),radius,2)
   pygame.draw.circle(layer,col,(c,c),radius-28,2)
   pygame.draw.circle(layer,col,(c,c),radius-70,1)

   for i in range(12):
      a=angle+i*math.tau/12
      p1=(c+math.cos(a)*(radius-70),c+math.sin(a)*(radius-70))
      p2=(c+math.cos(a)*radius,c+math.sin(a)*radius)
      pygame.draw.line(layer,col,p1,p2,2)

   points=[]

   for i in range(4):
      a=-angle*1.5+i*math.tau/4+math.pi/4

      points.append((c+math.cos(a)*(radius-28),c+math.sin(a)*(radius-28)))

   pygame.draw.polygon(layer,col,points,2)
   surface.blit(layer,(cx-c,cy-c))
   
def create_stone(x,y):
   stone={
      "x":x,
      "y":y,
      "base_y":y,
      "phase":random.uniform(0,math.tau)
   }
   return stone
      
def create_particle(x,y,vx,vy,life,color,size):
   particle={
      "x":x,
      "y":y,
      "vx":vx,
      "vy":vy,
      "life":life,
      "max_life":life,
      "color":color,
      "size":size
   }
   return particle

def create_rift(x,gap_y,gap_h):
   teeth_top=[random.randint(8,30) for _ in range(n+1)]
   teeth_bottom=[random.randint(8,30) for _ in range(n+1)]
   rift={
      "x":x,
      "gap_y":gap_y,
      "gap_h":gap_h,
      "teeth_top":teeth_top,
      "teeth_bottom":teeth_bottom,
      "passed":False
   }

   return rift

rifts.append(create_rift(width+50,last_gap_y,base_gap))

for _ in range(14):
   shards.append(create_shard(first=True))
  
while running:

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        
        if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
           running=False
        
        if event.type==pygame.KEYDOWN and game_state=="dead":
                if pygame.time.get_ticks()-dead_time>350:
                   player_y=height//2
                   player_velocity_y=thrust
                   rifts=[]
                   stones=[]
                   last_gap_y=(height-base_gap)//2
                   score=0
                   slow_timer=0
                   time_factor=1.0
                   new_record=False
                   game_state="playing"

                   continue
        if event.type==pygame.KEYDOWN:
                if event.key in(pygame.K_SPACE,pygame.K_UP,pygame.K_w):
                   if game_state=="ready":
                     game_state="playing"
                     player_velocity_y=thrust

                   elif game_state=="playing":
                     player_velocity_y=thrust

                    

                   

        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
           if game_state=="ready":
             game_state="playing"
             player_velocity_y=thrust

           elif game_state=="playing":
             player_velocity_y=thrust

           elif game_state=="dead":
              if pygame.time.get_ticks()-dead_time>350:
                 player_y=height//2
                 player_velocity_y=thrust
                 rifts=[]
                 stones=[]
                 last_gap_y=(height-base_gap)//2
                 score=0
                 slow_timer=0
                 time_factor=1.0
                 new_record=False
                 game_state="playing"

    


    rune_angle+=0.004

    for particle in particles:
       particle["x"]+=particle["vx"]
       particle["y"]+=particle["vy"]
       particle["life"]-=1

    particles=[particle for particle in particles if particle["life"]>0]




    for shard in shards:
       shard["x"]-=shard["speed"]
       if shard["x"]<-shard["size"]:
          new_shard=create_shard()
          shard.update(new_shard)

    if game_state=="playing":
      if slow_timer>0:
         slow_timer-=1
         target_factor=slow_factor
      else:
         target_factor=1.0
      time_factor+=(target_factor-time_factor)*0.08
      
      player_velocity_y=min(player_velocity_y+gravity,max_fall)
      player_y+=player_velocity_y
      rift_speed_now=current_speed(score)*time_factor
      for rift in rifts:
         rift["x"]-=rift_speed_now

      for stone in stones:
         stone["x"]-=rift_speed_now
         ticks=pygame.time.get_ticks()
         stone["y"]=stone["base_y"]+math.sin(ticks/250+stone["phase"])*10

      for rift in rifts:
         if not rift["passed"] and rift["x"]+rift_width<player_x:
            rift["passed"]=True
            score+=1

      if not rifts or rifts[-1]["x"]<=width-rift_spacing+50:
         gap_h=current_gap(score)

         lo=void_edge+40
         hi=height-void_edge-40-gap_h

         new_gap_y=last_gap_y+random.randint(-max_gap_shift,max_gap_shift)
         new_gap_y=max(lo,min(hi,new_gap_y))

         last_gap_y=new_gap_y

         if not rifts:
            new_x=width+50
         else:
            new_x=rifts[-1]["x"]+rift_spacing

            if rifts and not stones and random.random()<stone_chance:
               previous_rift=rifts[-1]
               previous_gap_center=previous_rift["gap_y"]+previous_rift["gap_h"]/2
               new_gap_center=new_gap_y+gap_h/2

               stone_x=new_x-rift_spacing/2+rift_width/2
               stone_y=(previous_gap_center+new_gap_center)/2

               stones.append(create_stone(stone_x,stone_y))
               

         rifts.append(create_rift(new_x,new_gap_y,gap_h))

      rifts=[
         rift for rift in rifts
         if rift["x"]>-rift_width
        ]

      cloak_angle=-player_velocity_y*3
      cloak_angle=max(-30,min(40,cloak_angle))
      player_rect=pygame.Rect(0,0,34,24)
      player_rect.center=(player_x,player_y)

      for stone in stones:
         stone_rect=pygame.Rect(0,0,32,32)
         stone_rect.center=(int(stone["x"]),int(stone["y"]))

         if player_rect.colliderect(stone_rect):
            slow_timer=int(slow_seconds*FPS)
            stones.remove(stone)
            break
       

      if player_rect.bottom>=height-void_edge or player_rect.top<=void_edge:
        game_state="dead"
        dead_time=pygame.time.get_ticks()
        check_high_score()
        for _ in range(40):
           angle=random.uniform(0,math.tau)
           speed=random.uniform(1,7)
           particles.append(create_particle(player_x,player_y,math.cos(angle)*speed,math.sin(angle)*speed,random.randint(25,50),random.choice([(170,20,30),ember,(255,224,150)]),random.randint(3,7)))


      for rift in rifts:
       top_rect=pygame.Rect(int(rift["x"]),0,rift_width,rift["gap_y"])
       bottom_y=rift["gap_y"]+rift["gap_h"]

       bottom_rect=pygame.Rect(int(rift["x"]),bottom_y,rift_width,height-bottom_y)

       if player_rect.colliderect(top_rect) or player_rect.colliderect(bottom_rect):
          game_state="dead"
          dead_time=pygame.time.get_ticks()
          check_high_score()
          for _ in range(40):
              angle=random.uniform(0,math.tau)
              speed=random.uniform(1,7)
              particles.append(create_particle(player_x,player_y,math.cos(angle)*speed,math.sin(angle)*speed,random.randint(25,50),random.choice([(170,20,30),ember,(255,224,150)]),random.randint(3,7)))

          break


    screen.fill(background)

    draw_rune_circle(screen,width//2,height//2,260,rune_angle)

    for shard in shards:
       points=[(shard["x"]+px,shard["y"]+py)
               for px,py in shard["points"]]
       
       pygame.draw.polygon(screen,shard["color"],points)

    for particle in particles:
       radius=max(1,int(particle["size"]*particle["life"]/particle["max_life"]))
       pygame.draw.circle(screen,particle["color"],(int(particle["x"]),int(particle["y"])),radius)

    for stone in stones:
       sx=int(stone["x"])
       sy=int(stone["y"])

       pulse=18+int(4*math.sin(pygame.time.get_ticks()/150))
       pygame.draw.circle(screen,(80,255,140),(sx,sy),pulse,2)
       diamond=[(sx,sy-14),(sx+10,sy),(sx,sy+14),(sx-10,sy)]
       pygame.draw.polygon(screen,(40,180,90),diamond)
       pygame.draw.polygon(screen,(150,255,180),diamond,2)


    pygame.draw.rect(screen,void_color,(0,0,width,void_edge))
    pygame.draw.rect(screen,void_color,(0,height-void_edge,width,void_edge))

    pygame.draw.line(screen,ember,(0,void_edge),(width,void_edge),3)
    pygame.draw.line(screen,ember,(0,height-void_edge),(width,height-void_edge),3)


    for rift in rifts:
       rift_x=rift["x"]
       rift_gap_y=rift["gap_y"]
       rift_gap_h=rift["gap_h"]

       teeth_top=rift["teeth_top"]
       teeth_bottom=rift["teeth_bottom"]

       top_points=[(rift_x,void_edge),(rift_x+rift_width,void_edge)]

       for i in range(n+1):
          px=rift_x+rift_width-i*rift_width/n
          if i%2==1:
             py=rift_gap_y-teeth_top[i]
          else:
             py=rift_gap_y
          top_points.append((px,py))

       pygame.draw.polygon(screen,(60,8,14),top_points)
       pygame.draw.polygon(screen,ember,top_points,3)
       pygame.draw.polygon(screen,(255,224,150),top_points,1)

       bottom_points=[(rift_x,height-void_edge),(rift_x+rift_width,height-void_edge)]

       for i in range(n+1):
          px=rift_x+rift_width-i*rift_width/n
          if i%2==1:
             py=(rift_gap_y+rift_gap_h+teeth_bottom[i])
          else:
             py=rift_gap_y+rift_gap_h
          bottom_points.append((px,py))

       pygame.draw.polygon(screen,(60,8,14),bottom_points)
       pygame.draw.polygon(screen,ember,bottom_points,3)
       pygame.draw.polygon(screen,(255,224,150),bottom_points,1)
        

   

    if game_state=="playing":
      rotated_cloak=pygame.transform.rotate(cloak_image,cloak_angle)
      cloak_rect=rotated_cloak.get_rect(center=(player_x,player_y))

      screen.blit(rotated_cloak,cloak_rect)

      score_text=font_big.render(str(score),True,(255,224,150))
      score_rect=score_text.get_rect(center=(width//2,75))
      screen.blit(score_text,score_rect)
    #   pygame.draw.rect(screen,player_color,(player_x,player_y,player_width,player_height))

      high_score_text=font_mid.render(f"High Score : {high_score}",True,(255,224,150))
      high_score_rect=high_score_text.get_rect(topright=(width-20,void_edge+10))

      screen.blit(high_score_text,high_score_rect)

    
    if game_state=="ready":
       veil=pygame.Surface((width,height),pygame.SRCALPHA)
       veil.fill((0,0,0,120))
       screen.blit(veil,(0,0))

       title=font_title.render("Rift Runner",True,(255,224,150))
       title_rect=title.get_rect(center=(width//2,190))
       screen.blit(title,title_rect)

       description=font_small.render("Guide the Cloak of Levitattion throgh the collapsing rifts",True,(245,240,230))
       description_rect=description.get_rect(center=(width//2,260))
       screen.blit(description,description_rect)

       controls=font_mid.render("SPACE/UP/W/CLICK=thrust",True,(245,240,230))
       controls_rect=controls.get_rect(center=(width//2,340))
       screen.blit(controls,controls_rect)

       start_text=font_small.render("Press any thrust key to begin",True,(240,90,50))
       start_rect=start_text.get_rect(center=(width//2,400))
       screen.blit(start_text,start_rect)

       floating_y=height/2+ 12*math.sin(pygame.time.get_ticks()/300)
       rotated_cloak=pygame.transform.rotate(cloak_image,0)
       cloak_rect=rotated_cloak.get_rect(center=(220,floating_y))
       screen.blit(rotated_cloak,cloak_rect)



    if game_state=="dead":
       veil=pygame.Surface((width,height),pygame.SRCALPHA)
       veil.fill((0,0,0,120))
       screen.blit(veil,(0,0))
       text=font_big.render("The Cloak is Lost",True,(255,224,150))
       text_rect=text.get_rect(center=(width//2,200))
       screen.blit(text,text_rect)

       score_text=font_mid.render(f"Final Score:{score}",True,(245,240,230))
       score_rect=score_text.get_rect(center=(width//2,280))
       screen.blit(score_text,score_rect)

       high_score_text=font_mid.render(f"High Score:{high_score}",True,(255,224,150))
       high_score_rect=high_score_text.get_rect(center=(width//2,320))
       screen.blit(high_score_text,high_score_rect)

       restart_text=font_small.render("Press any key to restart the timeline",True,(240,90,50))
       restart_rect=restart_text.get_rect(center=(width//2,350))
       screen.blit(restart_text,restart_rect)

    

    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()
