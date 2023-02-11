import os, github
import sys
import PyUtils, git



class GitHubAccount:
    def __init__(self, rootDir, argc, argv):
        self._argc = argc
        self._argv = argv
        self._account = "CharlesCarley"
        self._home = PyUtils.Path(os.path.abspath(rootDir))
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

    def repoBaseName(self, repo):
        name = repo.name
        loc = name.find('.')
        if loc != -1:
            loc+=1
            name = name[loc:]
        return name


    def clone(self):
        self.home().goto()
        repos = self.home().create("repos")
        repos.goto()

        print("Cloning into", self.home())

        cloneList = self.repos()
        for repo in cloneList.values():
            rn = self.repoBaseName(repo)
            repos.run("git clone %s %s"%(repo.ssh_url, rn))
        self.home().goto()

    def clean(self):
        self.home().goto()
        repos = self.home().create("repos")
        repos.remove()
        self.home().goto()
        self.home().run("ls")
 
    def pull(self):
        self.home().goto()
        repos = self.home().create("repos")
        repos.goto()

        cloneList = self.repos()
        for repo in cloneList.values():
            rn = self.repoBaseName(repo)
            repos.run("git clone %s %s"%(repo.ssh_url, rn))
            repos.subdir(rn).goto().run("python gitupdate.py")
            repos.goto()

    def build(self):
        self.home().goto()
        repos = self.home().create("repos")
        repos.goto()

        cloneList = self.repos()
        for repo in cloneList.values():
            rn = self.repoBaseName(repo)
            bd  = repos.subdir(rn).goto().create("build").goto()
            bd.run("cmake -D%s_BUILD_TEST=ON -D%s_AUTO_RUN_TEST=ON .."%(rn, rn))
            bd.run("cmake --build .")
            repos.goto()


    def findOpt(self, opt):
        for i in range(self._argc):
            if (opt == self._argv[i]):
                return True
        return False

    def usage(self):
        print("build <kind> <options>")
        print("")
        print("  Where <kind> is one of the following")
        print("")
        print("  clone  - clones the repositories in .tokens/repos.txt")
        print("  pull   - updates submodules for the repositories in .tokens/repos.txt")
        print("  clean  - removes the repos directory")
        print("  build  - builds and tests all repositories")
        print("  help   - displays this message")
        print("")
        print("")


def main(argc, argv):
    mgr = GitHubAccount(
        os.path.abspath(os.getcwd()),
        argc, 
        argv)

    if (mgr.findOpt("clone")):
        mgr.clone()
    elif (mgr.findOpt("pull")):
        mgr.pull()
    elif (mgr.findOpt("clean")):
        mgr.clean()
    elif (mgr.findOpt("all")):
        mgr.build()
    else:
        mgr.usage()

if __name__ == '__main__':
    main(len(sys.argv), sys.argv)
