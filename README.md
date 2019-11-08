Minimal Mistakes remote theme starter
=====================================

Fork this repo for the quickest method of getting started with the [Minimal Mistakes Jekyll theme](https://github.com/mmistakes/minimal-mistakes).

Contains basic configuration to get you a site with:

-	Sample posts.
-	Sample top navigation.
-	Sample author sidebar with social links.
-	Sample footer links.
-	Paginated home page.
-	Archive pages for posts grouped by year, category, and tag.
-	Sample about page.
-	Sample 404 page.
-	Site wide search.

Replace sample content with your own and [configure as necessary](https://mmistakes.github.io/minimal-mistakes/docs/configuration/).

---

Troubleshooting
---------------

If you have a question about using Jekyll, start a discussion on the [Jekyll Forum](https://talk.jekyllrb.com/) or [StackOverflow](https://stackoverflow.com/questions/tagged/jekyll). Other resources:

-	[Ruby 101](https://jekyllrb.com/docs/ruby-101/)
-	[Setting up a Jekyll site with GitHub Pages](https://jekyllrb.com/docs/github-pages/)
-	[Configuring GitHub Metadata](https://github.com/jekyll/github-metadata/blob/master/docs/configuration.md#configuration) to work properly when developing locally and avoid `No GitHub API authentication could be found. Some fields may be missing or have incorrect data.` warnings.

Local using rbenv
=================

clone
-----

```
git clone --origin mm-github-pages-starter https://github.com/mmistakes/mm-github-pages-starter timetemp_gh-pages
cd timetemp_gh-pages
# make edits and commit
git checkout -b timetemp
git remote add origin git@github.com:idcrook/timetemp.git
git remote update
git merge --allow-unrelated-histories --strategy ours origin/gh-pages
git checkout origin/gh-pages
git merge timetemp
```

install and run
---------------

```shell
cd timetemp_gh-pages
rbenv global
bundle install --path vendor/bundle
export PAGES_REPO_NWO=idcrook/timetemp
bundle exec jekyll serve
```
