import carla
import random
import time

def spawn_pedestrian_at_location(x, y, speed):
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.load_world('Town06')

    world = client.get_world()
    spectator = world.get_spectator() 

    actor_list = []
    try:
        # Connect to CARLA server
        
        # Load the blueprint library
        blueprint_library = world.get_blueprint_library()

        world.set_pedestrians_seed(1235)
        ped_bp = random.choice(world.get_blueprint_library().filter("walker.pedestrian.*"))
        spawn_location = carla.Location(x=x, y=y, z=1)
        transform = carla.Transform(spawn_location)

        ped = world.spawn_actor(ped_bp, transform)
        walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
        controller = world.spawn_actor(walker_controller_bp, carla.Transform(), ped)
        dest_location = carla.Location(x=x-100, y=y, z=0.5)

        controller.start()

        controller.go_to_location(dest_location)
        controller.set_max_speed(1.2)

        

        actor_list.append(controller)

        while True:
            world.tick()
            trans = ped.get_transform()

            transform = carla.Transform(ped.get_transform().transform(carla.Location(x=0,z=20)), carla.Rotation(yaw=0, pitch=-90,roll=90)) 
            spectator.set_transform(transform) 
            print("trans ped : ",trans)
            print("check")
        
    except RuntimeError as e:
        print(f"Runtime error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # time.sleep(5)
        print('destroying actors.')
        for actor in actor_list:
            actor.destroy()
if __name__ == "__main__":
    spawn_pedestrian_at_location(12.8, -35.7, 1.0)