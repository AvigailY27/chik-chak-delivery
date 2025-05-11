#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <stdlib.h>

void *print_message_function( void *ptr );

int call_some_threads(printer_t done)
{
  time_t t;
  srand((unsigned) time(&t));
  pthread_t thread1, thread2;
  int  iret1, iret2;

  iret1 = pthread_create( &thread1, NULL, print_message_function, (void*) done);
  iret2 = pthread_create( &thread2, NULL, print_message_function, (void*) done);

  pthread_join( thread1, NULL);
  pthread_join( thread2, NULL); 

  printf("Thread 1 returns: %d\n",iret1);
  printf("Thread 2 returns: %d\n",iret2);
  return 0;
}

void *print_message_function( void *ptr )
{
  int waittime = rand() % 10;
  sleep(waittime);
  printf("[%d]\n",  waittime);
  printer_t callback = (printer_t) ptr;
  callback(waittime);
  return NULL;
}