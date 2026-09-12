import modules
import schedule

schedule.every(1).minutes.do(modules.compute_data)

while True:
    schedule.run_pending()

