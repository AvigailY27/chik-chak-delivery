// path.c
#include <stdio.h>
#include <stdlib.h>
// Create a doubly linked list node for each point
typedef struct Node {
    double x, y;
    struct Node *prev, *next;
} Node;

typedef struct list {
    Node *head;
    Node *tail;
} list;
Node *head = NULL, *tail = NULL;

//כל שתי ערכים עוקבים במערך מייצגים נקודה אחת (לדוגמה, (x, y)).
//בנית רשימה דו כיוונית מהכתובות של הנקודות במערך

void populateList(double *coords, int length) {
    for (int j = 0; j < length; j += 2) {
        Node *new_node = (Node *)malloc(sizeof(Node));
        if (!new_node) {
            perror("Failed to allocate memory");
            return;
        }
        new_node->x = coords[j];
        new_node->y = coords[j + 1];
        new_node->prev = tail;
        new_node->next = NULL;

        if (tail) {
            tail->next = new_node;
        } else {
            head = new_node;
        }
        tail = new_node;
        printf("head: %p, tail: %p\n", head, tail);
    }
}
// Function to print the list for debugging purposes
void debugPrintList() {
    Node *current = head;
    printf("Debugging List:\n");
    while (current) {
        printf("Node at %p -> (%.2f, %.2f), prev: %p, next: %p\n", 
               current, current->x, current->y, current->prev, current->next);
        current = current->next;
    }
    printf("End of List\n");
}
#include <math.h>



// Function to check if adding a point delays travel time
int isTravelTimeAcceptable(Node *current, Node *candidate, Node *destination) {
    // Placeholder logic for travel time check
    // Replace with actual logic as needed
    double currentToCandidate = calculateDistance(current->x, current->y, candidate->x, candidate->y);
    double candidateToDestination = calculateDistance(candidate->x, candidate->y, destination->x, destination->y);
    double currentToDestination = calculateDistance(current->x, current->y, destination->x, destination->y);

    return (currentToCandidate + candidateToDestination) <= (currentToDestination * 1.2); // Example threshold
}

// Function to find and connect nearby points
Node *connectNearbyPoints(Node *current, Node *destination, double range) {
    Node *candidate = head;
    Node *closest = NULL;
    double closestDistance = range;

    while (candidate) {
        if (candidate != current && candidate != destination) {
            double distance = calculateDistance(current->x, current->y, candidate->x, candidate->y);
            if (distance <= range && isTravelTimeAcceptable(current, candidate, destination)) {
                if (distance < closestDistance) {
                    closest = candidate;
                    closestDistance = distance;
                }
            }
        }
        candidate = candidate->next;
    }

    if (closest) {
        // Connect the closest point to the current node
        closest->prev = current;
        closest->next = current->next;
        if (current->next) {
            current->next->prev = closest;
        }
        current->next = closest;
    }

    return current;
}

void printList() {
    Node *current = head;
    while (current) {
        printf("Point: (%.2f, %.2f)\n", current->x, current->y);
        current = current->next;
    }
}
//צריך לקבל קוריננטה ולפי זה לשלוח אותה ולקבל עליה פרטים של האילוצים ודרך, ואז לבדוק אם מה שחזר את הזמן נסיעה, עומס מרחק וכדומה
// Function to free the allocated memory for the list
void freeList() {
    Node *current = head;
    while (current) {
        Node *temp = current;
        current = current->next;
        free(temp);
    }
    head = tail = NULL;
}

// // Main function to demonstrate the functionality
int main() {
    
    printf("Program started\n");
    // Example coordinates array
    double coords[] = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0};
    int length = sizeof(coords) / sizeof(coords[0]);

    // Populate the list with the coordinates
    populateList(coords, length);

    // Print the list
    printf("Printing the list:\n");
    printList();

    // Debug print the list
    debugPrintList();

    // Free the allocated memory
    freeList();
    return 0;
}