---
title: How I built this blog without much coding
published: true
---

Two days back, I started planning to build my own blogging site. Since it was a calm weekend, I had enough time to explore various ways I can try to build my own blogging site. Most of the initial solutions that came to my mind involved building a full fledged blogging application on my own that involved many fancy features like Database, user registration, comments, likes, views count, interactive content etc. However, soon I decided not to go about it because that would be an overkill for what I am intending to do. My requirements to be precise (at a high level) were as follows:

1. Create a blog without much coding and it must be done in few hours, so I can enjoy my weekend.
2. Should be easy to add new posts every now and then - as easy as just creating a new file for every post.
3. Pagination - this was an important requirement because I wanted the viewers to see few posts at a time in chronological order without bombarding their UI with all the available posts in a single list (this would also increase the overall load time as the blog grows)
4. Should support markdown syntax - because it has good expressability while maintaining simplicity.  
5. Easy to deploy and publish - in other words I wanted something like a CI/CD mechanism that is deeply integrated with platforms like GitHub, because I wanted to use [Github-Pages](https://pages.github.com/) for serving my blog.

Going further in this post, I will be explaining how each of these requirements was satisfied. After exploration and quick googling I found this tool called [jekyll](https://jekyllrb.com/), to my surprise, it more of less supported all my requirements (with some additions).

### Jekyll to the rescue:
Jekyll is a Ruby package that allows us to write content as plain text (of course using Markdown - as per requirement 4) and transform it into a static website without having to worry much on build one from scratch (as per requirement 1). It also allows for customization by adding our own styles, header, footer etc. To my surprise, GitHub provides capabilities to build github-pages with Jekyll, they even have a well established [workflow](https://github.com/marketplace/actions/jekyll-deploy-gh-pages) that listens for commits, automatically trigger the build process and publishes the site with new changes (as per requirement 5). We also have many plugins built for Jekyll - thank god we also have a [pagination](https://jekyllrb.com/docs/pagination/) plugin (as per requirement 3).

### 1. Getting Started - Create a GitHub Repository and enable gh-pages:
This is fairly easy, if you have used GithHub before, most probably this will be like a cake-walk for you.
1. Check to this [tutorial](https://docs.github.com/en/get-started/quickstart/create-a-repo) to create a new repository.
2. Check this [tutorial](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) to enable gh-pages feature for the repository you created.

In my case, I wanted all the codebase related to my blog to be under `gh-pages` branch and not under `main` or `master`, so I selected `gh-pages` as the source branch. GitHub also provides some pre-configured themes for your site, I selected `hacker` theme, because I am a hacker fanboy - who grew up watching `Matrix` and `Mr.Robot`. 

Once done, clone the repository to make modifications locally and test it out, In my case it was:
```sh
# clone the repository
git clone git@github.com:<your-username>/<your-repo-name>.git
# don't forget to check gh-pages branch
git checkout gh-pages
```
### 2. Installing Ruby, Gem and Jekyll locally
To test your blog locally you might need to install Ruby and other tools, this will be useful during the initial stages because you will be making lot of changes to the codebase. Run these commands to install Ruby (I use ubuntu, if you are on a different Linux distribution based on Red-Hat or other operating system - you can refer to [this](https://www.ruby-lang.org/en/documentation/installation/) page.)

**On Ubuntu 20.04+:**
```sh
# start with an update (just to stay updated)
sudo apt update
# install ruby (gem will be installed along Ruby), We get tools like gcc, g++ and make via build-essential
sudo apt install ruby-full build-essential zlib1g-dev
```
To make sure you are all set, just check ruby and gen versions.
```sh
ruby -v
# on my system, it shows: ruby 2.7.2p137 (2020-10-01 revision 5445e04352) [x86_64-linux-gnu] (can be different on your machine based on architecture and OS you are using)

gem -v
# 3.2.5 (on my machine)
```
`gem` or [RubyGems](https://rubygems.org/) is a package manager for Ruby, just like how we have `npm`, `pip` and `cargo` for Node, Python and Rust. Jekyll must be [downloaded as a gem package](https://jekyllrb.com/docs/installation/), so we use `gem` command to do that. But for building the website locally we need lot of other tools, [github-pages gem](https://github.com/github/pages-gem) provides these tools for us, `jekyll` is also packaged along with this gem. So we need to install only `github-pages` gem.

```sh
# use sudo if you are getting permission error
gem install github-pages
```

### 3. Configure your blog
Once jekyll and other tools are installed, we can set-up your blog. The easiest way is to clone [my repository](https://github.com/Narasimha1997/blog) and checkout the `gh-pages` branch. Then copy the contents of my repository to your repository (under `gh-pages`), i.e
```sh
# clone my repo
git clone git@github.com:Narasimha1997/blog.git
cd blog
# checkout gh-pages branch
git checkout gh-pages
# remove all my existing posts
rm -r _posts/*.md
cp -r . /path/to/your/repo
```
Now go back to your project directory and edit the `_config.yml` file according to your needs. The current `_config.yml` looks like this:
```yml
# title and description of the site (will be used in <title> tag)
title: Narasimha Prasanna HN
description: Software Developer - Python, JavaScript, Go, Rust
# use hacker theme
theme: jekyll-theme-hacker
# this is the base URL (use http://localhost:4000/blog/ to access locally)
baseurl: /blog
plugins:
  # use paginator plugin
  - jekyll-paginate
defaults:
  -
    scope:
      path: ""
      type: "posts"
    values:
      layout: "post"
source: .
destination: ./_site
permalink: /:title
# display 3 posts in a page
paginate: 3
paginate_path: /page/:num/
# this will be displayed as the banner of the blog's home page
banner: "root@prasanna-desktop:~#"
# your linkedin profile
linkedin: https://in.linkedin.com/in/narasimha-prasanna-hn-17aa89146
# your Github profile
github: https://github.com/Narasimha1997
# your portfolio
portfolio: http://prasannahn.ml/
```
The comments in this file will guide you to understand the meaning of each parameter. Once modified, you should be able to serve your blog locally. Run:
```
jekyll serve
```
Then you should be able to view the site at `http://localhost:4000/blog/`. Jekyll supports live-reloading, so you can view your changes reflected on the site without running `jekyll serve` command again.

### 4. Publish your blog to Github:
Once you are satisfied with the configuration, stage your changes, make local commit and push it to the remote branch (i.e `gh-pages`). This can be done by executing following commands:
```sh
git add .
git commit -m "<some nice message>"
git push origin gh-pages
```
Now go to the repository on Github, you will see that a workflow has been triggered, this workflow will perform almost similar steps you did locally and deploys the website. Once the workflow is complete you can check your blog live at: `https://<your-username>.github.io/<your-repo-name>` for me it is `https://Narasimha1997.github.io/blog`, which you can view [here](https://Narasimha1997.github.io/blog).
