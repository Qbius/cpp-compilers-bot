from cpp_reference import get_cpp_features_map, compare_to_current
from discord_bot_interface import command, task, run, create_state, client
from discord import Embed

@command
def subscribe(message, state):
    state.subs.add(message.author.id)
    return "Subscribed!"

@command
def unsubscribe(message, state):
    state.subs.remove(message.author.id)
    return "Unsubscribed!"

@task.loop(seconds = 60)
def check_cpp_reference(state):
    new_features = compare_to_current(state.features)
    if new_features:
        return [client.get_user(usr_id).send(embed = Embed(description = new_features)) for usr_id in state.subs]

run(default_state = create_state(subs = set(), features = get_cpp_features_map()))