#include <iostream>

using namespace std;

int main() {
    int x = 5;

    {
        int x;
        int y = 12;
        x = 7;
        cout << "Inside the block x=" << x << endl;
        cout << "Inside the block y=" << y << endl;
    }

    cout << "Outside the block x=" << x << endl;
    // You can't do this: cout << "Outside the block y=" << y << endl;
    // y is not defined the current lexical scope
}