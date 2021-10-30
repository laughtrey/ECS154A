import random
from math import log

def sequential_read(out_file_name, num_reads, offset, num_address_bits, num_data_bits):
	"""
	Creates a sequential read sequence for the Logisim Cache project beginning at offset.
	@out_file_name: the name of the output file
	@num_reads: the number of sequential reads to do
	@offset: how far into memory to begin the reading
	@num_address_bits: the number of address bits
	@num_data_bits: the number of data bits
	"""
	with open(out_file_name, 'w') as out_file:
		out_file.write('v2.0 raw\n')
		read = 1 << (num_address_bits +  num_data_bits + 1)
		done = 1 << (num_address_bits +  num_data_bits + 1 + 1)
		for i in range(offset, offset+num_reads):
			address = i << num_data_bits
			out_file.write('%x #read addr %d\n' % ((read | address), i))
			
		out_file.write('%x #do nothing\n' % (0)) #just a quick pause
		out_file.write('%x #complete testing and do nothing\n' % (done))
			

def sequential_write(out_file_name, num_writes, offset, value_offset, 
		num_address_bits, num_data_bits, num_sets, num_ways, line_size):
	"""
	Creates a sequential write sequence for the Logisim Cache project beginnning at offset.
	@out_file_name: the name of the output file
	@num_writes: the number of sequential reads to do
	@offset: how far into memory to begin the reading
	@value_offset: what the starting data value should be 
	@num_address_bits: the number of address bits
	@num_data_bits: the number of data bits
	@num_sets: the number of sets
	@num_ways: the number of lines per set
	@line_size: the size of each line
	"""
	with open(out_file_name, 'w') as out_file:
		out_file.write('v2.0 raw\n')
		num_line_bits = int(log(line_size,2))
		num_set_bits = int(log(line_size,2))
		read = 1 << (num_address_bits +  num_data_bits + 1)
		write = 1 << (num_address_bits +  num_data_bits)
		done = 1 <<(num_address_bits +  num_data_bits + 1 + 1)
		for i in range(offset, offset+num_writes):
			address = i << num_data_bits
			value = (value_offset + i) % (2**num_data_bits)
			out_file.write('%x #write value 0x%x to addr %d \n' % ((write | address | value), value, i))
		
		#flush the cache to see if the values were updated.
		for set in range(num_sets): #for each set
			selected_set = set << (num_data_bits + num_line_bits)
			for way in range(0,num_ways): #for each way in the set
				tag = way << (num_data_bits + num_line_bits + num_set_bits)
				for i in range(2): #guarentee we knock out that line to memory
					tag += i << (num_data_bits + num_line_bits + num_set_bits)
					address = tag | selected_set
					out_file.write('%x #read addr %d\n' % ((read | address), address >> num_data_bits))
					
		#read everything back in to see if we updated correctly
		for i in range(offset, offset+num_writes):
			address = i << num_data_bits
			out_file.write('%x #read addr %d\n' % ((read | address), i))
					
		out_file.write('%x\n' % (0)) #just a quick pause
		out_file.write('%x\n' % (done)) #mark that we are completed
			
def targeted_set_read(out_file_name, num_set_reads, which_set,
	num_address_bits, num_sets, line_size, num_data_bits):
	"""
	Creates a read sequence that continually accesses
	the same set over and over again for the Logisim Cache project.
	Reads are done sequentially starting from the beginning of memory
	@out_file_name: the name of the output file
	@num_set_reads: the number of reads to do
	@which_set: which set are we trying to keep hitting
	@num_address_bits: the number of address bits
	@num_sets: the number of sets in the cache. must be a power of 2
	@line_size: the number of elements per line. must be a power of 2
	@num_data_bits: the number of data bits
	"""
	with open(out_file_name, 'w') as out_file:
		out_file.write('v2.0 raw\n')
		num_line_bits = int(log(line_size,2))
		num_set_bits = int(log(line_size,2))
		read = 1 << (num_address_bits +  num_data_bits + 1)
		done = 1 << (num_address_bits +  num_data_bits + 1 + 1)
		the_set = which_set << (num_data_bits + num_line_bits)
		for i in range(num_set_reads):
			address = i << (num_data_bits + num_set_bits + num_line_bits) #get the tag for the address we want to make
			for j in range(line_size):
				element = j << num_data_bits
				address |= the_set | element
				out_file.write('%x #read addr %d\n' % ((read | address), address >> num_data_bits))
			#out_file.write('\n')
		out_file.write('%x\n' % (0)) #just a quick pause
		out_file.write('%x\n' % (done))
			

def targeted_set_write(out_file_name, num_set_writes, which_set,
	value_offset, num_address_bits, num_sets, line_size, num_data_bits):
	"""
	Creates a read sequence that continually accesses
	the same set over and over again for the Logisim Cache project.
	Reads are done sequentially starting from the beginning of memory
	@out_file_name: the name of the output file
	@num_set_reads: the number of reads to do
	@which_set: which set are we trying to keep hitting
	@value_offset: the first data value to write
	@num_address_bits: the number of address bits
	@num_sets: the number of sets in the cache. must be a power of 2
	@line_size: the number of elements per line. must be a power of 2
	@num_data_bits: the number of data bits
	"""
	with open(out_file_name, 'w') as out_file:
		out_file.write('v2.0 raw\n')
		num_line_bits = int(log(line_size,2))
		num_set_bits = int(log(line_size,2))
		read = 1 << (num_address_bits +  num_data_bits + 1)
		write = 1 << (num_address_bits +  num_data_bits)
		done = 1 << (num_address_bits +  num_data_bits + 1 + 1)
		the_set = which_set << (num_data_bits + num_line_bits)
		for i in range(num_set_writes):
			address = i << (num_data_bits + num_set_bits + num_line_bits)
			for j in range(line_size):
				value_offset %= (2**num_data_bits)
				element = j << num_data_bits
				address |= the_set | element
				out_file.write('%x #write value 0x%x to addr %d \n' % 
				((write | address | value_offset), value_offset, address >> num_data_bits))
				value_offset += 1
		
		#read in the values we just wrote out
		for i in range(num_set_writes):
			address = i << (num_data_bits + num_set_bits + num_line_bits) #get the tag for the address we want to make
			for j in range(line_size):
				element = j << num_data_bits
				address |= the_set | element
				out_file.write('%x\n' % (read | address))
			#out_file.write('\n')
		out_file.write('%x\n' % (0)) #just a quick pause
		out_file.write('%x\n' % (done))
		
def constrained_random_read_write(out_file_name, 
																	num_reads_and_writes, max_address, 
																	num_address_bits, num_data_bits):
	"""
	Creates a read sequence that randomly accesses addressses between 0 and max_address inclusive
	@out_file_name: the name of the output file to be created
	@num_reads_and_writes: the total number of reads and writes to do
	@max_address: the maximum address that can be generated
	@num_address_bits: the number of address_bits
	@num_data_bits: the size of each data element
	"""
	
	with open(out_file_name, 'w') as out_file, open('random0_sim_inputs.txt', 'w') as rand_sim_out:
		read =  1 << (num_address_bits + num_data_bits + 1)
		write = 1 << (num_address_bits + num_data_bits)
		done =  1 << (num_address_bits + num_data_bits + 1 + 1)
		cmds = [read,write]
		
		out_file.write('v2.0 raw\n') #write header
		for read_or_write in range(num_reads_and_writes):
			cmd = random.choice(cmds) #pick a command to do
			address = random.randint(0, max_address) << num_data_bits #generate the address
			value = random.randint(0, (2**num_data_bits) - 1) #generate the value to be written if we do a write
			out_file.write('%x ' % (cmd | address | value)) #generate the command in the out file
			if cmd == read:
				out_file.write('#read addr %d' % (address >> num_data_bits))
				rand_sim_out.write('r %d\n' % (address >> num_data_bits))
			else:
				out_file.write('#write value 0x%x to addr %d' % (value, (address >> num_data_bits)))
				rand_sim_out.write('w %d %d\n' % ((address >> num_data_bits), value))
			out_file.write('\n')
		rand_sim_out.write('q\n')
			
		
		out_file.write('%x #do nothing\n' % (0)) #just a quick pause
		out_file.write('%x #complete testing and do nothing\n' % (done))	
			

def make_sequential_mem(out_file_name, num_address_bits, num_data_bits):
	"""
	Creates a memory file for the logisim cache project
	@out_file_name: the name of the output file
	@num_address_bits: the number of address bits
	@num_data_bits: the number of data bits
	"""
	with open(out_file_name, 'w') as out_file:
		out_file.write('v2.0 raw\n')
		count = 0
		for i in range(2**num_address_bits):
			value = 0
			for j in range(4):
				value |= count << (j*8)
				count += 1
				count %= 2**8
				
			out_file.write('%08x\n' % value)

def make_random_mem(out_file_name, seed, num_address_bits, num_data_bits):
	"""
	Creates a memory file for the logisim 
	@out_file_name: the name of the output file
	@seed: the seed to the random number generator
	@num_address_bits: the number of address bits
	@num_data_bits: the number of data bits
	"""
	with open(out_file_name, 'w') as out_file:
		random.seed(seed)
		out_file.write('v2.0 raw\n')
		for i in range(2**num_address_bits):
			out_file.write('%08x\n' % random.randint(0, 2**num_data_bits - 1))

def make_solution(out_file_name, command_file_name, mem_file_name,
									num_address_bits, num_data_bits):
	with open(out_file_name, 'w') as out_file, open(command_file_name) as cmd_fil:
		mem = read_mem_file(mem_file_name)
		correct_count = 0
		read = 1 << (num_address_bits +  num_data_bits + 1) #read bit
		write = 1 << (num_address_bits +  num_data_bits)
		read_set = 1 << num_data_bits #to set if we are doing a read
		data_mask = int('1'*num_data_bits, 2)
		addr_mask = int('1'*num_address_bits, 2) << num_data_bits
		out_file.write('v2.0 raw\n')
		out_file.write("#Test input file name: %s\n" % command_file_name)
		out_file.write("#Memory file name: %s\n" % mem_file_name)
		#out_file.write('0\n') #first line is 0 because before first clock tick we haven't done anything
		cmd_fil.readline() #skip the header
		for cmd in cmd_fil:
			cmd = cmd.split('#')[0] #keep only the part before the comments
			cmd = int(cmd,16)
			address = (cmd & addr_mask) >> num_data_bits
			data = cmd & data_mask
			
			if cmd & read: #doing a write
				out_file.write( '%x\n' % (read_set | mem[address]))
				correct_count += 1
			elif cmd & write: #doing a write
				mem[address] = data 
				out_file.write('%x\n' % mem[address])
			else: #doing nothing
				out_file.write('0\n')
		
		out_file.write('#Final correct count: %d\n' % correct_count)

def read_mem_file(mem_file_name):
	with open(mem_file_name) as mem_fil:
		mem = []
		mem_fil.readline() #skip the header
		for line in mem_fil:
			line = line.strip() #remove 
			for i in range(len(line), 0, -2):
				mem.append(int(line[i-2:i],16))
		return mem
			
		
	
def main():
	
	#make_sequential_mem('seq_mem.txt', 8, 32)
	#make_random_mem('rand_mem.txt', 1, 8, 32)
	random.seed(1)
	
	#sequential_read('seq_read1.txt', 24, 0, 10, 8)
	#make_solution('seq_read1_seq_mem_sol.txt', 'seq_read1.txt', 'seq_mem.txt', 10, 8)
	
	#sequential_write('seq_write1.txt', 24, 0, 5, 10, 8, 2, 3, 4)
	#make_solution('seq_write1_seq_mem_sol.txt', 'seq_write1.txt', 'seq_mem.txt', 10, 8)
	
	
	#targeted_set_read('set1_targeted_read.txt', 6, 1, 10, 2, 4, 8)
	#make_solution('set1_targeted_read_seq_mem_sol.txt', 'set1_targeted_read.txt', 'seq_mem.txt', 10, 8)
	
	#targeted_set_write('set0_targeted_write.txt', 6, 0, 5, 10, 2, 4, 8)
	#make_solution('set0_targeted_write_seq_mem_sol.txt', 'set0_targeted_write.txt', 'seq_mem.txt', 10, 8)
	
	constrained_random_read_write('random0.txt',24*4, 24*2 - 1, 10, 8)
	#make_solution('random0_seq_mem_sol.txt', 'random0.txt', 'seq_mem.txt', 10, 8)
	
	#constrained_random_read_write('final_test.txt',24*6, 24*3 - 1, 10, 8)
	#make_solution('final_test_rand_mem_sol.txt', 'final_test.txt', 'rand_mem.txt', 10, 8)
	
main()

		
