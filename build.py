import os, github
import sys
import PyUtils
import PyUtils.Colors as c



class GitHubAccount:
    def __init__(self, rootDir, argc, argv):
        self._argc = argc
        self._argv = argv
        self._home = PyUtils.Path(os.path.abspath(rootDir))
        self._cred = self.home().subdir(".tokens")
        self._account = self._accountHolder()

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
            print(c.r, "Failed to read access token", c.reset)
        return token

    def _accountHolder(self):
        usr = None
        try:
            fp = self.credentials().open("user.txt")
            usr = fp.read()
            fp.close()
        except IOError:
            print("Failed to read user")
        return usr

    def _repos(self):
        lines = []
        try:
            fp = self.credentials().open("repos.txt")
            rl = fp.readlines()
            for line in rl:
                rpo = line.replace("\r", "").replace("\n", "")
                if (len(rpo) > 0):
                    if (rpo.startswith('#')): continue
                    lines.append(rpo)
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
                repoList[repo.name] = repo
        return repoList


    def _maxNameLen(self):
        wanted = self._repos()
        m = 0
        for r in wanted: m = max(m, len(r))
        return m


    def repoBaseName(self, repo):
        name = repo.name
        loc = name.find('.')
        if loc != -1:
            loc += 1
            name = name[loc:]
        return name



    def listRepos(self):
        print(c.g+"Repositories:", c.reset)

        self.home().goto()
        repos = self.repos()
        mr = self._maxNameLen()

        for repo in repos.values():
            print(repo.name.ljust(mr, ' '), "->", repo.ssh_url)


    def clone(self):
        self.home().goto()
        repos = self.home().create("repos")
        repos.goto()

        print("Cloning into", self.home())
        cloneList = self.repos()
        for repo in cloneList.values():
            rn = self.repoBaseName(repo)
            repos.run("git clone %s %s" % (repo.ssh_url, rn))
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

            print("")
            print(c.y+"  Pulling repository ", c.g0, repo.ssh_url, c.reset)
            print("")
            print("")


            repos.run("git clone %s %s" % (repo.ssh_url, rn))
            print("")
            print(c.y+"  Executing git update", c.reset)
            print("")
            print("")
            repos.subdir(rn).goto().run("python gitupdate.py")
            repos.goto()

    def sync(self):
        self.clean()
        self.home().goto()
        repos = self.home().create("repos")
        repos.goto()

        cloneList = self.repos()
        for repo in cloneList.values():
            rn = self.repoBaseName(repo)
            repos.run("git clone %s %s" % (repo.ssh_url, rn))
            rd = repos.subdir(rn).goto()
            rd.run("python gitupdate.py")
            rd.run("git commit -a -m \"Update sub-modules\"")
            rd.run("git push")
            repos.goto()


    def build(self):
        self.home().goto()
        repos = self.home().create("repos")
        repos.goto()

        cloneList = self.repos()
        for repo in cloneList.values():
            rn = self.repoBaseName(repo)
            print("")
            print(c.r+"  Building repository ", c.g0, repo.ssh_url, c.reset)
            print("")
            print("")

            bd = repos.subdir(rn).goto().create("build").goto()
            bd.run("cmake --build .")
            repos.goto()


    def config(self):
        self.home().goto()
        repos = self.home().create("repos")
        repos.goto()

        cloneList = self.repos()
        for repo in cloneList.values():
            rn = self.repoBaseName(repo)
            bd = repos.subdir(rn).goto().create("build").goto()
            print("")
            print(c.r+"  Configuring repository ", c.g0, repo.ssh_url, c.reset)
            print("")
            print("")

            bd.run("cmake -D%s_BUILD_TEST=ON -D%s_AUTO_RUN_TEST=ON .." %
                   (rn, rn))
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
        print("  pull   - updates submodules from .tokens/repos.txt")
        print("  clean  - removes the repos directory")
        print("  all    - builds and tests all repositories")
        print("  config - configures all repositories with cmake")
        print("  sync   - synchronizes all repositories to the master branch")
        print("")
        print("")
        print("  ls     - lists pullable repos")
        print("  help   - displays this message")
        print("")
        print("")


def main(argc, argv):
    mgr = GitHubAccount(os.path.abspath(os.getcwd()), argc, argv)
    if (mgr.findOpt("clone")):
        mgr.clone()
    elif (mgr.findOpt("pull")):
        mgr.pull()
    elif (mgr.findOpt("clean")):
        mgr.clean()
    elif (mgr.findOpt("all")):
        mgr.build()
    elif (mgr.findOpt("config")):
        mgr.config()
    elif (mgr.findOpt("sync")):
        mgr.sync()
    elif (mgr.findOpt("ls")):
        mgr.listRepos()
    elif (mgr.findOpt("everything")):
        mgr.clean()
        mgr.pull()
        mgr.config()
        mgr.build()
    else:
        mgr.usage()


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)
