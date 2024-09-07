% This is a demonstration of saving variables to a transfer file from Matlab.
# For making the transfer() function available, follow the steps in the README.md 

close all
clear all
syms x varphi
% varphi is used here to be correctly parsed in LaTeX
chr = (x^2 + 1/x*varphi);
a = 'test.txt';
b = 2.5675;
c = "45";
d_3 = [13; 15; 149; 132]
t = 1==0
f = 1==1

transfer(a,b,c,chr,d_3,t,f)