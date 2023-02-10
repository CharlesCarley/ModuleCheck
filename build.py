import os, github

class GitHubAccount:
    def __init__(self, rootDir):
        self.account = "CharlesCarley"
        self.github = ""
        self.home = rootDir

    def getPublicRepoList(self):
        os.chdir(self.home)
        gh = github.Github()

        repos = gh.get_user().get_repos()

        repoList = {}
        for repo in repos:
            if (repo.fork): continue
            if (repo.owner.login != self.account): continue
            if (repo.private): continue

            repoList[repo.name] = repo.clone_url

        return repoList;

    

def main():
    mgr = GitHubAccount(os.path.abspath(os.getcwd()))
    mgr.getPublicRepoList()





    

if __name__=='__main__':
    main()
