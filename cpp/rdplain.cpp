#include<iostream>
#include<fstream>
#include<boost/circular_buffer.hpp>
#include<assert.h>
#include<functional>
#include<chrono>

int stackDepth = 99; //maximum reuse distance [0-stackDepth]
boost::circular_buffer<unsigned long long> cb(stackDepth);

// print the circular buffer
int printcb() {
  for(auto& I:cb) {
   std::cout << I << "\n";
  }
}

void printHistogram(std::vector<int>& hist) {
  int index = 0;
  for(auto& I:hist) {
    std::cout << "hist[" << index << "] : "<<I<<"\n";
    index++;
  }
}

// prints the histogram in terms of %
void prettyPrintHistogram(std::vector<int>& hist) {
  int index = 0;
  int sum = std::accumulate(hist.begin(), hist.end(), 0);
  for(auto& I:hist) {
    std::cout << "hist[" << index << "] : "<<(I*100.0)/sum<<"\n";
    index++;
  }
}

// checks for address in the cb, returns iterator to it if found 
boost::circular_buffer<unsigned long long>::iterator find(unsigned long long address) {
  boost::circular_buffer<unsigned long long>::iterator I = cb.begin(), E=cb.end();
  for(; I!=E; I++) {
    if(*I == address) {
      return I;
    }
  }
  
  // element is not found.
  return E;
}
                    
int main(int argc, char** argv){

  if(argc !=2 ) {
    std::cout << "Usage: ./rdplain.cpp [full path to input]\n";
    exit(1);
  }

  //std::cout << "Stack based reuse-distance calculation\n";
  std::ifstream fd(argv[1]);
  std::vector<int> histogram(stackDepth+1, 0);
  std::string line;
  std::chrono::time_point<std::chrono::system_clock> start, end;
  start = std::chrono::system_clock::now();

  if (fd.is_open())
  {
    while (getline(fd, line))
    {
      unsigned long long address = std::stoll(line);
      boost::circular_buffer<unsigned long long>::iterator it = find(address);
      int distance = stackDepth;

      // this address already exists in the buffer. We need to move it to the top
      if(it != cb.end()) {
        distance = std::distance(it, cb.end()) - 1;
        cb.erase(it);
      }
       
      assert(distance>=0);
      histogram[distance]++;
      cb.push_back(address);
    }

    fd.close();
  }
  else std::cout << "Unable to open input file"; 

  //printcb();
  //printHistogram(histogram);
  prettyPrintHistogram(histogram);
  end = std::chrono::system_clock::now();
  std::chrono::duration<double> elapsed_seconds = end-start;
  //std::cout<<"Program duration : "<< elapsed_seconds.count() << "(s)\n";

  return 0;
}
