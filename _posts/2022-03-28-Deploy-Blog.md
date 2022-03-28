---
title: How I built this blog without much coding
published: true
---

Two days back, I started planning to build my own blogging site. Since it was a calm weekend, I had enough time to explore various ways I can try to build my own blogging site. Most of the initial solutions that came to my mind involved building a full fledged blogging application on my own that involved many fancy features like Database, user registration, comments, likes, views count, interactive content etc. However, soon I decided not to go about it because that would be an overkill for what I am intending to do. My requirements to be precise (at a high level) were as follows:

1. Create a blog without much coding and it must be done in few hours, so I can enjoy my weekend.
2. Should be easy to add new posts every now and then - as easy as just creating a new file for every post.
3. Pagination - this was an important requirement because I wanted the viewers to to see few posts at a time in chronological order without bombarding their UI with all the available posts in a single list (this would also increase the overall load time as the blog grows)
4. Should support markdown syntax - because it has good express-ability while maintaining simplicity.  
5. Easy to deploy and publish - in other words I wanted something like a CI/CD mechanism that is deeply integrated with platforms like GitHub, because I wanted to use [Github-Pages](https://pages.github.com/) for serving my blog.

Going further in this post, I will be explaining how each of these requirements was satisfied. After exploration and quick googling I found this tool called [jekyll](https://jekyllrb.com/), to my surprise, it more of less supported all my requirements (with some additions).

#### Jykell to the rescue:
Jykell is a Ruby package that allows us to write content as plain text (of course using Markdown - as per requirement 4) and transform it into a static website without having to worry much on build one from scratch (as per requirement 1). It also allows for customization by adding our own styles, header, footer etc. To my surprise, GitHub provides capabilities to build github-pages with Jykell, they even have a well established [workflow](https://github.com/marketplace/actions/jekyll-deploy-gh-pages) that listens for commits, automatically trigger the build process and publishes the site with new changes (as per requirement 5). We also have many plugins built for Jykell - thank god we also have a [pagination](https://jekyllrb.com/docs/pagination/) plugin (as per requirement 3).

#### 1. Getting Started - Create a GitHub Repository and enable gh-pages:
This is fairly easy, if you have used GithHub before, most probably this will be like a cake-walk for you.
1. Check to this [tutorial](https://docs.github.com/en/get-started/quickstart/create-a-repo) to create a new repository.
2. Check this [tutorial](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) to enable gh-pages feature for the repository you created.

In my case, I wanted all the codebase related to my blog to be under `gh-pages` branch and not under `main` or `master`, so I selected `gh-pages` as the source branch. GitHub also provides some pre-configured themes for your site, I selected `hacker` theme, because I am a hacker fanboy - who grew up watching `Matrix` and `Mr.Robot`. 

Once done, clone the repository to make modifications locally and test it out, In my case it was:
```sh
# clone the repository
git clone git@github.com:Narasimha1997/blog.git
# don't forget to check gh-pages branch
git checkout gh-pages
```
#### 2. Installing Ruby, Gem and Jykell locally
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
# on my system, it shows: ruby 3.1.1p18 (2022-02-18 revision 53f5fc4236) [x86_64-linux (can be different on your machine based on architecture and OS you are using)

gem -v
# 3.3.7 (on my machine)
```
`gem` or [RubyGems](https://rubygems.org/) is a package manager for Ruby, just like how we have `npm`, `pip` and `cargo` for Node, Python and Rust. Jykell must be [downloaded as a gem package](https://jekyllrb.com/docs/installation/), so we use `gem` command to do that.

```sh
# use sudo if you are getting permission error
gem install jekyll
```
