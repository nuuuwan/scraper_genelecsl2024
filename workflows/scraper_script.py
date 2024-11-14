import os
import shutil
import time

from utils import Log

from common_local_state import CommonLocalState
from scraper import ECLK

log = Log("ScraperScript")


class LocalAppUser:
    LOCAL_APP_PATH = os.path.join(
        "C:/Users",
        "ASUS",
        "Not.Dropbox",
        "CODING",
        "js_react",
        "election",
    )
    LOCAL_APP_FILE_DB_FILE = os.path.join(
        "public",
        "data",
        "elections",
        # "government-elections-parliamentary.regions-ec.2024.tsv",
        "government-elections-presidential.regions-ec.2024.tsv",
    )

    LOCAL_APP_FILE_DB_PATH = os.path.join(
        LOCAL_APP_PATH, LOCAL_APP_FILE_DB_FILE
    )


class ScriptCommand:
    def __str__(self):
        return self.__class__.__name__


class Script:
    def run(self):
        for i, command in enumerate(self.commands, start=1):
            print("")

            log.info(f"{i}) Running {command}")

            try:
                command.run()
            except Exception as e:
                log.error(e)
                log.warning("🛑 STOPPED!")
                print("-" * 64)
                break

            log.info("✅ DONE!")
            print("-" * 64)

    def run_forever(self, time_wait=60):
        while True:
            self.run()
            log.debug(f"😴 Sleeping {time_wait}s...")
            time.sleep(time_wait)


class ECLKScrape(ScriptCommand):
    def run(self):
        eclk = ECLK()
        eclk.election


class CommonLocalStateUpdate(ScriptCommand):
    def run(self):
        CommonLocalState.update()


class LocalAppFileDBCopy(ScriptCommand, LocalAppUser):
    def run(self):
        src_path = ECLK.get_election_path()
        dst_path = self.LOCAL_APP_FILE_DB_PATH
        shutil.copyfile(src_path, dst_path)
        log.debug(f"Copied {src_path} to {dst_path}")


class LocalAppToRemoteAppPushDeploy(ScriptCommand, LocalAppUser):
    def run(self):
        cmd_list = [
            f"cd {self.LOCAL_APP_PATH}",
            f"git add {self.LOCAL_APP_FILE_DB_FILE}",
            'git commit -m "Copied Data"',
            "git push origin main",
        ]
        cmd = " && ".join(cmd_list)
        log.debug(f"Running {cmd}")

        os.system(cmd)


class ScraperScript(Script):
    @property
    def commands(self):
        return [
            ECLKScrape(),
            CommonLocalStateUpdate(),
            LocalAppFileDBCopy(),
            LocalAppToRemoteAppPushDeploy(),
        ]


if __name__ == "__main__":
    ScraperScript().run_forever()