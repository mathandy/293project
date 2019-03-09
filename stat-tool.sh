# Problems 1 and 2
# use stat to get execution times for 1 and 4 threads
export n_samples=3
export measurement=real
binary=o0x264
echo '' > t1.txt && echo '' > t4.txt

for i in $(seq 1 $n_samples); do 
	(time ./$binary --threads=4 -o junk soccer_4cif_30fps.y4m) 2>> t4.txt
	(time ./$binary --threads=1 -o junk soccer_4cif_30fps.y4m --threads=1) 2>> t1.txt
	echo $i; 
done
cat t4.txt | grep $measurement > tt4.txt && cat t1.txt | grep $measurement > tt1.txt &&
python -c "ts = [60*float(l.split()[1][0]) + float(l.split()[1][2:-1]) for l in open('tt1.txt')]; m = sum(ts)/len(ts); s = (sum((t-m)**2 for t in ts)/(len(ts)-1))**.5; print '\n1threads -- $binary:\nmean =', m, 's\nstd =', s, 's'" &&
python -c "ts = [60*float(l.split()[1][0]) + float(l.split()[1][2:-1]) for l in open('tt4.txt')]; m = sum(ts)/len(ts); s = (sum((t-m)**2 for t in ts)/(len(ts)-1))**.5; print '\n4threads -- $binary:\nmean =', m, 's\nstd =', s, 's'"