import os, github
import Utils



class GitHubAccount:
    def __init__(self, rootDir):
        self._account = "CharlesCarley"
        self._home = Utils.Path(os.path.abspath(rootDir))
        self._cred = self.home().subdir(".tokens")

    def home(self):
        return self._home
    def credentials(self):
        return self._cred

    def _token(self, name):
        token = None
        try:
            fp = self.credentials().open(name)
            token = fp.read()
            fp.close()
        except IOError:
            print("Failed to read access token")
        return token

    def _repos(self):
        lines = []
        try:
            fp = self.credentials().open("repos.txt")
            rl = fp.readlines()
            for line in rl:
                lines.append(line.replace("\r", "").replace("\n", ""))
            fp.close()
        except IOError:
            print("Failed to read repo list")

        return lines

    def _public(self):
        return self._token("pub.txt")

    def repos(self):
        gh = github.Github(self._public())
        repos = gh.get_user().get_repos()

        wanted = self._repos()

        repoList = {}
        for repo in repos:
            if (repo.fork): continue
            if (repo.owner.login != self._account): continue
            if repo.name in wanted:
                print("".ljust(2, ' '), "repository:", repo.name)
                repoList[repo.name] = repo
        return repoList

    def clone(self):
        self.home().goto()
        print("Cloning into", self.home())

        cloneList = self.repos()
        for repo in cloneList.values():
            if (not os.path.isdir(repo.name)):
                self.home().run("git clone %s" %repo.ssh_url)
            else:
                print("Skipping", repo.name, ":", repo.ssh_url)
                print("".ljust(2, ' '), "directory exists")

        self.home().goto()

    def removeRepos(self):
        self.home().goto()

        cloneList = self.repos()
        for repo in cloneList.values():
            print("removing repo.name ", repo.name)
            self.home().subdir(repo.name).remove()

        self.home().goto()
 


def main():
    mgr = GitHubAccount(os.path.abspath(os.getcwd()))
    mgr.clone()
    mgr.removeRepos()


if __name__ == '__main__':
    main()
