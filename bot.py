from discord_bot_interface import event, command, task, run

@command
def subscribe(hehe, state):
    state.hehe = hehe

@command
def get(state):
    return state.hehe

run()