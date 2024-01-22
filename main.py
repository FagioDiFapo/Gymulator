import gymnasium as gym
from huggingface_sb3 import load_from_hub, package_to_hub
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor
from lunar_lander import LunarLander

#envs = make_vec_env(LunarLander, n_envs=16)
#model = PPO(
#    policy = 'MlpPolicy',
#    env = envs,
#    n_steps = 1024,
#    batch_size = 64,
#    n_epochs = 4,
#    gamma = 0.999,
#    gae_lambda = 0.98,
#    ent_coef = 0.01,
#    verbose=1,
#    device="cuda")
#
#model.learn(total_timesteps=1000000)
#model_name = "ppo-RocketLander"
#model.save(model_name)

#eval_env = Monitor(gym.make("RocketLander", render_mode="human"))
eval_env = LunarLander(render_mode = "human")
model = PPO.load("ppo-RocketLander.zip")
mean_reward, std_reward = evaluate_policy(model, eval_env, n_eval_episodes=10, deterministic=True)
print(f"mean_reward={mean_reward:.2f} +/- {std_reward}")
