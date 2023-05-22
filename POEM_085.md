POEM ID: 085  
Title: Export view_connections to csv   
Author: crecine (Carl Recine)   
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: 2925  

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated

Motivation
==========

When comparing the connections created by different branches/commits, it can be hard to find differences when switching back and forth between tabs.
Exporting the conection list as a csv allows it to be sorted, filtered, etc by csv editors like Excel and allows for text-based diffs.
This is particularly useful for debugging large models with many connections.

Description
===========

An argument should be added to view_connections to allow for exporting as a csv.
This could be:
- True/False option in addition to always creating the html file
- A string html/csv/both
- A string or list of strings
- Part of the filename

I think the last option (filename) would be best.
The default filename would remain connections.html and the updated function would be backwards commpatible with current usage.
If the filename contains .csv instead of .html, view_connections would save the results to a csv instead of an html file.
This would make the options "show_browser" and "title" have no effect; however, they are optional and specifying them wouldn't be an issue.
