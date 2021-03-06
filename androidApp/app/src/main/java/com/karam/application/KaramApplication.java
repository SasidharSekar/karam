package com.karam.application;

import android.app.Application;

import androidx.work.ExistingPeriodicWorkPolicy;
import androidx.work.OneTimeWorkRequest;
import androidx.work.PeriodicWorkRequest;
import androidx.work.WorkManager;
import androidx.work.WorkRequest;

import com.karam.service.NotifyWorker;

import java.util.concurrent.TimeUnit;

/**
 * Warning: Do not store anything that you wish to persist in this class
 * The data can be lost if the system crashes and restarts or if the
 * Application goes to the background and comes back.
 **/

/**
 * Extends the whole application class
 */
public class KaramApplication extends Application {
    /**
     * FIXME: NEW_COMER: Implement notification
     * This is just a test function
     * Enqueues a periodic notification request
     */
    private void testPeriodicNotify() {
        WorkManager workManager = WorkManager.getInstance(this);
        PeriodicWorkRequest w = new PeriodicWorkRequest.Builder(NotifyWorker.class, 15, TimeUnit.MINUTES).build();
        workManager.enqueueUniquePeriodicWork("s", ExistingPeriodicWorkPolicy.KEEP, w);
    }

    /**
     * FIXME: NEW_COMER: Implement notification
     * This is just a test function
     * Enqueues a one time notification request
     */
    private void testOneTimeNotify() {
        WorkManager workManager = WorkManager.getInstance(this);
        WorkRequest w = new OneTimeWorkRequest.Builder(NotifyWorker.class).build();
        workManager.enqueue(w);
    }

    /**
     * Called when the application is starting, before any other application objects have been created.
     */
    @Override
    public void onCreate() {
        super.onCreate();

        // TODO Use appLocale to set language
        // UserData userData = new UserData(getApplicationContext());
        // String lang = userData.get_current_language();
        // AppLocale.set_language(getApplicationContext(), lang);
        // TODO: Implement notification mechanism
        // Following 2 lines are just to test basic android notification
        // testOneTimeNotify();
        // testPeriodicNotify();
    }

    /**
     * TODO NEW_COMER
     * The function is called when the overall system is running low on memory,
     * and would like actively running processes to tighten their belts.
     * Overriding this method is totally optional!
     */
    @Override
    public void onLowMemory() {
        super.onLowMemory();
    }
}