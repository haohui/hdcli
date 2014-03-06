=====
HDCLI
=====

HDCLI is a collection of scripts to automate committing and resolving
HADOOP jiras. To use HDCLI, copy all files in conf-example/ into
~/.hdcli/ and customize config.yaml. You also need to check out the
branches and the trunk in the directory that <hadoop_repo_directory>
points to. For example:

  $ cd <hadoop_repo_directory>
  $ svn co https://svn.apache.org/repos/asf/hadoop/common/trunk trunk
  $ mkdir branches && cd branches
  $ svn co https://svn.apache.org/repos/asf/hadoop/common/branches/branch-2 branch-2

Enjoy committing :-)
