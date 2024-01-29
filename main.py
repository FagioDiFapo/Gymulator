import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor
from rocket_lander import RocketLander

# PPO TRAINING
#envs = make_vec_env(RocketLander, n_envs=16)
###envs = RocketLander(render_mode="human")
#model = PPO(
#    policy = 'MlpPolicy',
#    env = envs,
#    n_steps = 1024,
#    batch_size = 64,
#    n_epochs = 4,
#    gamma = 0.999,
#    gae_lambda = 0.98,
#    ent_coef = 0.05,
#    verbose=1,
#    device="cuda")
#
#model.learn(total_timesteps=1000000)
#model_name = "ppo-RocketLander1"
#model.save(model_name)

# EVALUATION RUN
eval_env = Monitor(RocketLander(render_mode = "human"))
#eval_env = LunarLander(render_mode = "human")
model = PPO.load("ppo-RocketLander1.zip")
mean_reward, std_reward = evaluate_policy(model, eval_env, n_eval_episodes=10, deterministic=True)
print(f"mean_reward={mean_reward:.2f} +/- {std_reward}")

# TEST RUN
#env = RocketLander(render_mode = "human")
#env.action_space.seed(42)
#
#observation, info = env.reset(seed=42)
#
#for _ in range(1000):
#    observation, reward, terminated, truncated, info = env.step(env.action_space.sample())
#
#    #print(observation)
#    print(reward)
#    if terminated or truncated:
#        observation, info = env.reset()
#
#env.close()